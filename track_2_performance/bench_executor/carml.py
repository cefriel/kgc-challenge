#!/usr/bin/env python3

"""
CARML is a reactive RML engine that transforms structured data sources into RDF
based on declarative RML mappings. Supports JSON, XML, CSV, and SQL sources.

**Website**: https://github.com/carml/carml
**Repository**: https://github.com/carml/carml
"""

import os
from typing import Optional
from timeout_decorator import timeout, TimeoutError  # type: ignore
from bench_executor.container import Container
from bench_executor.logger import Logger

VERSION = 'latest'
TIMEOUT = 3 * 3600  # 3 hours


class CARML(Container):
    """CARML container for executing RML mappings."""

    def __init__(self, data_path: str, config_path: str, directory: str,
                 verbose: bool):
        """Creates an instance of the CARML class.

        Parameters
        ----------
        data_path : str
            Path to the data directory of the case.
        config_path : str
            Path to the config directory of the case.
        directory : str
            Path to the directory to store logs.
        verbose : bool
            Enable verbose logs.
        """
        self._data_path = os.path.abspath(data_path)
        self._config_path = os.path.abspath(config_path)
        self._logger = Logger(__name__, directory, verbose)
        self._verbose = verbose

        os.makedirs(os.path.join(self._data_path, 'carml'), exist_ok=True)
        os.makedirs(os.path.join(self._data_path, 'carml-spill'), exist_ok=True)
        super().__init__(f'carml:{VERSION}', 'CARML',
                         self._logger,
                         environment={
                             'JAVA_TOOL_OPTIONS': '--add-opens=java.base/java.nio=ALL-UNNAMED -Xmx1g -Xms1g'
                         },
                         volumes=[f'{self._data_path}/carml:/data',
                                  f'{self._data_path}/shared:/data/shared',
                                  f'{self._data_path}/carml-spill:/carml-spill'])

    @property
    def root_mount_directory(self) -> str:
        """Subdirectory in the root directory of the case for CARML.

        Returns
        -------
        subdirectory : str
            Subdirectory of the root directory for CARML.
        """
        return __name__.lower()

    @timeout(TIMEOUT)
    def _execute_with_timeout(self, arguments: list) -> bool:
        """Execute a mapping with a provided timeout.

        Returns
        -------
        success : bool
            Whether the execution was successfull or not.
        """

        cmd = 'map --spill-to-disk --in-process-db-memory 1GB'
        if self._verbose:
            cmd += ' -v'
        cmd += f' {" ".join(arguments)}'

        self._logger.debug(f'Executing CARML with arguments '
                           f'{" ".join(arguments)}')

        return self.run_and_wait_for_exit(cmd)

    def execute(self, arguments: list) -> bool:
        """Execute CARML with given arguments.

        Parameters
        ----------
        arguments : list
            Arguments to supply to CARML.

        Returns
        -------
        success : bool
            Whether the execution succeeded or not.
        """
        try:
            return self._execute_with_timeout(arguments)
        except TimeoutError:
            msg = f'Timeout ({TIMEOUT}s) reached for CARML'
            self._logger.warning(msg)

        return False

    def execute_mapping(self,
                        mapping_file: str,
                        output_file: str,
                        serialization: str,
                        rdb_username: Optional[str] = None,
                        rdb_password: Optional[str] = None,
                        rdb_host: Optional[str] = None,
                        rdb_port: Optional[int] = None,
                        rdb_name: Optional[str] = None,
                        rdb_type: Optional[str] = None) -> bool:
        """Execute a mapping file with CARML.

        N-Quads and N-Triples are currently supported as serialization
        format for CARML.

        Parameters
        ----------
        mapping_file : str
            Path to the mapping file to execute.
        output_file : str
            Name of the output file to store the triples in.
        serialization : str
            Serialization format to use.
        rdb_username : Optional[str]
            Username for the database, required when a database is used as
            source.
        rdb_password : Optional[str]
            Password for the database, required when a database is used as
            source.
        rdb_host : Optional[str]
            Hostname for the database, required when a database is used as
            source.
        rdb_port : Optional[int]
            Port for the database, required when a database is used as source.
        rdb_name : Optional[str]
            Database name for the database, required when a database is used as
            source.
        rdb_type : Optional[str]
            Database type, required when a database is used as source.

        Returns
        -------
        success : bool
            Whether the execution was successfull or not.
        """
        # Map KROWN serialization names to CARML format flags
        serialization_map = {
            'ntriples': 'nt',
            'nquads': 'nq',
            'turtle': 'ttl',
        }
        fmt = serialization_map.get(serialization, 'nt')

        arguments = ['-m', os.path.join('/data/shared/', mapping_file),
                     '-r', '/data/shared',
                     '-F', fmt,
                     '-o', os.path.join('/data/shared/', output_file)]

        return self.execute(arguments)
