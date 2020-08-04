import os
from typing import List
from typing import Optional


class HostOptions:
    """Options for running a command on an emulated host."""

    def __init__(
        self,
        *,
        command: List[str],
        ros_setup_bash: Optional[os.PathLike] = None,
        ros_domain_id: Optional[int] = None,
        rmw_implementation: Optional[str] = None,
        localhost_only: bool = False,
    ):
        """
        Constructor.

        :param command: The command to run on the host.
        :param ros_setup_bash: Path to the setup.bash file of a ROS
           installation to use.
        :param ros_domain_id: The value to assign to the ROS_DOMAIN_ID
           environment variable.
        :param rmw_implementation: The identifier for the RMW implementation to use.
           Sets the RMW_IMPLEMENTATION environment variable to this value.
        """
        self.__command = []
        if ros_setup_bash is not None:
            self.__command += ['source', str(ros_setup_bash)]
        if ros_domain_id is not None:
            self.__command += ['&&', 'export', f'ROS_DOMAIN_ID={ros_domain_id}']
        if rmw_implementation is not None:
            self.__command += ['&&', 'export', f'RMW_IMPLEMENTATION={rmw_implementation}']
        if localhost_only:
            self.__command += ['&&', 'export', f'ROS_LOCALHOST_ONLY=1']

        if self.__command:
            self.__command += ['&&']
        self.__command += command

    @property
    def command(self):
        return self.__command
