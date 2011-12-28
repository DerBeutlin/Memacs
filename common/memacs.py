#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2011-12-28 20:22:49 armin>

import logging
import traceback
from common.argparser import MemacsArgumentParser
from common.orgwriter import OrgOutputWriter
from common.loggingsettings import handle_logging
import sys


class Memacs(object):
    """
    Memacs class

    With this class it is easier to make a Memacs module
    because it handles common things like
    * default arguments + parsing
        - orgoutputfile
        - version
        - verbose
        - suppress-messages
    * set logging information
        - write error logs to error.org_archive if
          orgfile is specified

    use handle_main() to start Memacs

    Testing:
    * use test_get_all()     for getting whole org output
    * use test_get_entries() for getting only org entries
    """

    def __init__(self,
                 prog_version="no version specified",
                 prog_version_date="no date specified",
                 prog_description="no description specified",
                 prog_short_description="no short-description specified",
                 prog_tag="no tag specified",
                 copyright_year="",
                 copyright_authors="",
                 argv=sys.argv[1:]):
        """
        Ctor

        Please set Memacs information like version, description, ...

        set argv when you want to test class

        set write_footer i

        """
        self.__prog_version = prog_version
        self.__prog_version_date = prog_version_date
        self.__prog_description = prog_description
        self.__prog_short_description = prog_short_description
        self.__prog_tag = prog_tag
        self.__writer_append = False
        self.__copyright_year = copyright_year
        self.__copyright_authors = copyright_authors
        self.__argv = argv

    def __init(self, test=False):
        """
        we use this method to initialize because here it could be, that
        Exceptions are thrown. in __init__() we could not catch them
        see handle_main() to understand

        @param test: used in test_get_all
        """
        self._parser = MemacsArgumentParser(
            prog_version=self.__prog_version,
            prog_version_date=self.__prog_version_date,
            prog_description=self.__prog_description,
            copyright_year=self.__copyright_year,
            copyright_authors=self.__copyright_authors)
        # adding additional arguments from our subcass
        self._parser_add_arguments()
        # parse all arguments
        self._parser_parse_args()
        # set logging configuration
        handle_logging(self._args.verbose,
                       self._args.suppressmessages,
                       self._args.outputfile)

        # for testing purposes it's good to see which args ar secified
        logging.debug("args specified:")
        logging.debug(self._args)

        # if an tag is specified as argument take that tag
        if self._args.tag:
            tag = self._args.tag
        else:
            tag = self.__prog_tag

        self._writer = OrgOutputWriter(
            file_name=self._args.outputfile,
            short_description=self.__prog_short_description,
            tag=tag,
            test=test,
            append=self._args.append)

    def _main(self):
        """
        does nothing in this (super) class
        this method should be overwritten by subclass
        """
        pass

    def _parser_add_arguments(self):
        """
        does nothing in this (super) class,
        In subclass we add arguments to the parser
        """
        pass

    def _parser_parse_args(self):
        """
        Let's parse the default arguments
        In subclass we have to do additional
        parsing on (the additional) arguments
        """
        self._args = self._parser.parse_args(self.__argv)

    def __get_writer_data(self):
        """
        @return org_file_data (only when on testing)
        """
        return self._writer.get_test_result()

    def handle_main(self):
        """
        this should be called instead of main()

        With this method we can catch exceptions
        and log them as error

        logging.error makes a org-agenda-entry too if a
        outputfile was specified :)
        """
        try:
            self.__init()
            self._main()
            self._writer.close()
        except KeyboardInterrupt:
            logging.info("Received KeyboardInterrupt")
        except SystemExit, e:
            # if we get an sys.exit() do exit!
            sys.exit(e)
        except:
            error_lines = traceback.format_exc().splitlines()
            logging.error("\n   ".join(map(str, error_lines)))
            raise  # re raise exception

    def test_get_all(self):
        """
        Use this for Testing

        @param return: whole org-file
        """
        self.__init(test=True)
        self._main()
        self._writer.close()
        return self.__get_writer_data()

    def test_get_entries(self):
        """
        Use this for Testing

        @param return: org-file without header +footer (only entries)
        """
        data = self.test_get_all()
        ret_data = []
        for d in data.splitlines():
            if d[:2] != "* " and d[:1] != "#":
                ret_data.append(d)
        return ret_data
