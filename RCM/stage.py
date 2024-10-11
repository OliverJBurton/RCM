# Import necessary libraries
import time  # Provides time-related functions
import serial  # Provides support for serial communication


class Controller:
    """
    A basic device adapter for Thorlabs MCM3000 and MCM3001 3-axis controllers.

    This class allows communication with Thorlabs motorized controllers via serial communication, providing 
    functionality to control the movement of connected stages.

    Not implemented:
    - Stop function (not useful?)
    - Query motor status (not working? documentation error?)

    Test code runs and seems robust.
    """

    def __init__(self,
                 which_port,
                 name='MCM3000',
                 stages=3 * (None,),  # e.g., ('None', 'None', 'ZFM2030')
                 reverse=3 * (False,),  # e.g., (False, False, True)
                 verbose=True,
                 very_verbose=False):
        """
        Initializes the Controller class by connecting to the specified COM port, setting the stage parameters, 
        and configuring movement options such as reverse directions and verbosity.

        Args:
            which_port (str): The serial port to which the controller is connected (e.g., 'COM4').
            name (str): The name of the controller (default is 'MCM3000').
            stages (tuple): Tuple defining the type of stages connected (e.g., ('ZFM2030', 'ZFM2030', 'ZFM2030')).
            reverse (tuple): Tuple specifying if the stage movements should be reversed (True/False).
            verbose (bool): Flag to enable/disable basic output logs.
            very_verbose (bool): Flag to enable/disable detailed output logs for debugging.

        Raises:
            IOError: If the controller is not connected or the COM port is unavailable.
        """
        self.name = name
        self.stages = stages
        self.reverse = reverse
        self.verbose = verbose
        self.very_verbose = very_verbose

        if self.verbose:
            print(f"{self.name}: opening...", end='')

        # Try opening the serial port with the specified baud rate and timeout
        try:
            self.port = serial.Serial(port=which_port, baudrate=460800, timeout=5)
        except serial.serialutil.SerialException:
            raise IOError(f'{self.name}: no connection on port {which_port}')

        if self.verbose:
            print(" done.")

        # Ensure stages and reverse parameters are tuples of correct length
        assert isinstance(self.stages, tuple) and isinstance(self.reverse, tuple)
        assert len(self.stages) == 3 and len(self.reverse) == 3
        for element in self.reverse:
            assert isinstance(element, bool)

        # Initialize internal variables for encoder counts and movement parameters
        self._encoder_counts = 3 * [None]
        self._encoder_counts_tol = 3 * [1]  # Tolerance in encoder counts (can hang if < 1 count)
        self._target_encoder_counts = 3 * [None]
        self._um_per_count = 3 * [None]
        self._position_limit_um = 3 * [None]
        self.position_um = 3 * [None]

        # Supported stages and their corresponding micrometers per encoder count and position limits
        supported_stages = {
            'ZFM2020': (0.2116667, 1e3 * 12.7),
            'ZFM2030': (0.2116667, 1e3 * 12.7),
            'MMP-2XY': (0.5, 1e3 * 25.4)
        }

        # Initialize channels for connected stages
        self.channels = []
        for channel, stage in enumerate(self.stages):
            if stage is not None:
                assert stage in supported_stages, f'{self.name}: stage "{stage}" not supported'
                self.channels.append(channel)
                self._um_per_count[channel] = supported_stages[stage][0]
                self._position_limit_um[channel] = supported_stages[stage][1]
                self._get_encoder_counts(channel)

        self.channels = tuple(self.channels)

        if self.verbose:
            print(f"{self.name}: stages:", self.stages)
            print(f"{self.name}: reverse:", self.reverse)
            print(f"{self.name}: um_per_count:", self._um_per_count)
            print(f"{self.name}: position_limit_um:", self._position_limit_um)
            print(f"{self.name}: position_um:", self.position_um)

    def _encoder_counts_to_um(self, channel, encoder_counts):
        """
        Converts encoder counts to micrometers (um) based on the channel's stage configuration.

        Args:
            channel (int): The axis (0, 1, or 2) for which to convert encoder counts.
            encoder_counts (int): The number of encoder counts to convert.

        Returns:
            float: The position in micrometers.

        If the reverse flag is set for the channel, the position is negated.
        """
        um = encoder_counts * self._um_per_count[channel]
        if self.reverse[channel]:
            um = - um + 0  # Avoid -0.0
        if self.very_verbose:
            print(f'{self.name}(ch{channel}): -> encoder counts {encoder_counts} = {um:.2f}um')
        return um

    def _um_to_encoder_counts(self, channel, um):
        """
        Converts micrometers (um) to encoder counts based on the channel's stage configuration.

        Args:
            channel (int): The axis (0, 1, or 2) for which to convert micrometers.
            um (float): The position in micrometers to convert.

        Returns:
            int: The corresponding encoder counts.

        If the reverse flag is set for the channel, the encoder counts are negated.
        """
        encoder_counts = int(round(um / self._um_per_count[channel]))
        if self.reverse[channel]:
            encoder_counts = - encoder_counts + 0  # Avoid -0.0
        if self.very_verbose:
            print(f'{self.name}(ch{channel}): -> {um:.2f}um = encoder counts {encoder_counts}')
        return encoder_counts

    def _send(self, cmd, channel, response_bytes=None):
        """
        Sends a command to the specified channel and optionally reads a response.

        Args:
            cmd (bytes): The command to send.
            channel (int): The channel (0, 1, or 2) to send the command to.
            response_bytes (int, optional): Number of bytes to read from the response.

        Returns:
            bytes or None: The response from the device, if any.

        Raises:
            AssertionError: If the specified channel is not available.
        """
        assert channel in self.channels, f'{self.name}: channel "{channel}" is not available'
        if self.very_verbose:
            print(f'{self.name}(ch{channel}): sending cmd: {cmd}')

        self.port.write(cmd)  # Send the command

        # If response is expected, read it
        response = self.port.read(response_bytes) if response_bytes is not None else None
        assert self.port.inWaiting() == 0  # Ensure the buffer is empty

        if self.very_verbose:
            print(f'{self.name}(ch{channel}): -> response: {response}')
        return response

    def _get_encoder_counts(self, channel):
        """
        Retrieves the current encoder counts for the specified channel.

        Args:
            channel (int): The axis (0, 1, or 2) to retrieve the encoder counts from.

        Returns:
            int: The current encoder counts for the specified channel.
        """
        if self.very_verbose:
            print(f'{self.name}(ch{channel}): getting encoder counts')

        # Prepare and send the command to retrieve encoder counts
        channel_byte = channel.to_bytes(1, byteorder='little')
        cmd = b'\x0a\x04' + channel_byte + b'\x00\x00\x00'
        response = self._send(cmd, channel, response_bytes=12)

        # Ensure the correct channel was selected in the response
        assert response[6:7] == channel_byte

        # Parse encoder counts from the response
        encoder_counts = int.from_bytes(response[-4:], byteorder='little', signed=True)

        if self.very_verbose:
            print(f'{self.name}(ch{channel}): -> encoder counts = {encoder_counts}')

        # Update internal state with the encoder counts
        self._encoder_counts[channel] = encoder_counts
        self.position_um[channel] = self._encoder_counts_to_um(channel, encoder_counts)
        return encoder_counts

    def _set_encoder_counts_to_zero(self, channel):
        """
        Resets the encoder counts for the specified channel to zero.

        WARNING: This assumes that the stage encoder is set to zero at the center of its range.

        Args:
            channel (int): The axis (0, 1, or 2) to reset.

        Returns:
            None
        """
        if self.verbose:
            print(f'{self.name}(ch{channel}): setting encoder counts to zero')

        # Prepare the command to set the encoder counts to zero
        channel_byte = channel.to_bytes(2, byteorder='little')
        encoder_bytes = (0).to_bytes(4, 'little', signed=True)
        cmd = b'\x09\x04\x06\x00\x00\x00' + channel_byte + encoder_bytes
        self._send(cmd, channel)

        # Wait until the encoder counts are set to zero
        while True:
            encoder_counts = self._get_encoder_counts(channel)
            if encoder_counts == 0:
                break

        if self.verbose:
            print(f'{self.name}(ch{channel}): -> done')

    def _move_to_encoder_count(self, channel, encoder_counts, block=True):
        """
        Moves the stage of the specified channel to a target encoder count.

        Args:
            channel (int): The axis (0, 1, or 2) to move.
            encoder_counts (int): The target encoder counts to move to.
            block (bool): If True, block until the move is complete.

        Returns:
            None
        """
        if self._target_encoder_counts[channel] is not None:
            self._finish_move(channel)

        if self.very_verbose:
            print(f'{self.name}(ch{channel}): moving to encoder counts = {encoder_counts}')

        self._target_encoder_counts[channel] = encoder_counts

        # Prepare and send the move command
        encoder_bytes = encoder_counts.to_bytes(4, 'little', signed=True)
        channel_bytes = channel.to_bytes(2, byteorder='little')
        cmd = b'\x53\x04\x06\x00\x00\x00' + channel_bytes + encoder_bytes
        self._send(cmd, channel)

        if block:
            self._finish_move(channel)

    def _finish_move(self, channel, polling_wait_s=0.1):
        """
        Waits until the movement of the specified channel is finished.

        Args:
            channel (int): The axis (0, 1, or 2) to monitor.
            polling_wait_s (float): Time (in seconds) to wait between polling.

        Returns:
            None
        """
        if self._target_encoder_counts[channel] is None:
            return

        while True:
            encoder_counts = self._get_encoder_counts(channel)
            if self.verbose:
                print('.', end='')  # Progress indicator

            time.sleep(polling_wait_s)
            target = self._target_encoder_counts[channel]
            tolerance = self._encoder_counts_tol[channel]

            # Check if the movement has finished
            if target - tolerance <= encoder_counts <= target + tolerance:
                break

        if self.verbose:
            print(f'\n{self.name}(ch{channel}): -> finished move.')

        self._target_encoder_counts[channel] = None

    def _legalize_move_um(self, channel, move_um, relative):
        """
        Ensures the requested movement is within the legal limits of the stage.

        Args:
            channel (int): The axis (0, 1, or 2) to move.
            move_um (float): The movement in micrometers.
            relative (bool): If True, the move is relative to the current position.

        Returns:
            float: The adjusted legal move in micrometers.
        """
        if self.verbose:
            print(f'{self.name}(ch{channel}): requested move_um = {move_um:.2f} (relative={relative})')

        if relative:
            move_um += self.position_um[channel]

        # Check if the move is within the position limits
        limit_um = self._position_limit_um[channel]
        assert -limit_um <= move_um <= limit_um, (
            f'{self.name}: ch{channel} -> move_um ({move_um:.2f}) exceeds position_limit_um ({limit_um:.2f})'
        )

        # Convert the move to encoder counts and back to micrometers
        move_counts = self._um_to_encoder_counts(channel, move_um)
        legal_move_um = self._encoder_counts_to_um(channel, move_counts)

        if self.verbose:
            print(f'{self.name}(ch{channel}): -> legal move_um = {legal_move_um:.2f} '
                  f'({move_um:.2f} requested, relative={relative})')

        return legal_move_um

    def move_um(self, channel, move_um, relative=True, block=True):
        """
        Moves the stage of the specified channel by the requested micrometer value.

        Args:
            channel (int): The axis (0, 1, or 2) to move.
            move_um (float): The movement in micrometers.
            relative (bool): If True, the move is relative to the current position.
            block (bool): If True, block until the move is complete.

        Returns:
            float: The final legal move in micrometers.
        """
        legal_move_um = self._legalize_move_um(channel, move_um, relative)

        if self.verbose:
            print(f'{self.name}(ch{channel}): moving to position_um = {legal_move_um:.2f}')

        encoder_counts = self._um_to_encoder_counts(channel, legal_move_um)
        self._move_to_encoder_count(channel, encoder_counts, block)

        if block:
            self._finish_move(channel)

        return legal_move_um

    def close(self):
        """
        Closes the serial connection to the controller and releases resources.

        Returns:
            None
        """
        if self.verbose:
            print(f"{self.name}: closing...", end=' ')

        self.port.close()

        if self.verbose:
            print("done.")


if __name__ == '__main__':
    """
    Test the Controller class with a connected device on a specific port.

    This section initializes the controller, performs relative and absolute movements, 
    and checks stage positions. Finally, the device connection is closed.
    """
    channel = 0
    controller = Controller(which_port='COM4',
                            stages=('ZFM2030', 'ZFM2030', 'ZFM2030'),
                            reverse=(False, False, True),
                            verbose=True,
                            very_verbose=False)

    # Reset zero position (uncomment to use):
    # controller.move_um(channel, 10)
    # controller._set_encoder_counts_to_zero(channel)
    # controller.move_um(channel, 0)

    print(f'\n# Position attribute = {controller.position_um[channel]:.2f}')

    print('\n# Home:')
    controller.move_um(channel, 0, relative=False)

    print('\n# Some relative moves:')
    for moves in range(3):
        controller.move_um(channel, 10)
    for moves in range(3):
        controller.move_um(channel, -10)

    print('\n# Legalized move:')
    legal_move_um = controller._legalize_move_um(channel, 100, relative=True)
    controller.move_um(channel, legal_move_um)

    print('\n# Some random absolute moves:')
    from random import randrange

    for moves in range(3):
        random_move_um = randrange(-100, 100)
        controller.move_um(channel, random_move_um, relative=False)

    print('\n# Non-blocking move:')
    controller.move_um(channel, 200, block=False)
    controller.move_um(channel, 100, block=False)
    print('(immediate follow-up call forces finish on pending move)')
    print('doing something else')
    controller._finish_move(channel)

    print('\n# Encoder tolerance check:')
    for i in range(3):
        controller.move_um(channel, 0, relative=False)
        controller.move_um(channel, 0.2116667, relative=False)

    # Close the connection to the device.
    controller.close()
