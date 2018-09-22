#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2012-03-09 15:48:38 armin>

import logging
import time
import PyPDF2
import os
import re
import datetime as dt
from collections import namedtuple
from .lib.orgproperty import OrgProperties
from .lib.orgformat import OrgFormat
from .lib.memacs import Memacs

RailwayTicket = namedtuple('RailwayTicket', ['stops', 'stop_times'])


class DBTicketParser:
    def __init__(self):
        pass

    def extract_text(self, path):
        with open(path, 'rb') as f:
            pdfReader = PyPDF2.PdfFileReader(f)
            page = pdfReader.getPage(0)
            text = page.extractText()
            return text

    def find_in_text(self, regex, text):
        compiled_regex = re.compile(regex)
        result = compiled_regex.search(text)
        if result is not None:
            return result.group(1).strip()

    def extract_date(self, text):
        regex = re.compile('(Hinfahrt|ckfahrt) am (\d{2}.\d{2}.\d{4})')
        result = regex.search(text)
        if result is not None:
            return dt.datetime.strptime(result.group(2).strip(),
                                        '%d.%m.%Y').date()

    def extract_stops(self, text, departure_date):
        days = [departure_date + dt.timedelta(days=i) for i in range(10)]
        split_pattern = 'HaltDatumZeit.*\n?Reservierung'
        text = re.split(split_pattern, text)[1]
        compiled_regex = re.compile(
            '([^\d\n]*)\n?(' + '|'.join([d.strftime('%d.%m.')
                                         for d in days]) + ')(ab|an)')
        results = compiled_regex.findall(text)
        return [stop[0] for stop in results]

    def extract_stop_times(self, text, stops, departure_date):
        stop_times = []
        for stop in set(stops):
            compiled_regex = re.compile(
                re.escape(stop) + '\n?(\d{2}.\d{2}).(ab|an)\s(\d{2}:\d{2})')
            results = compiled_regex.findall(text)
            for r in results:
                day, month = r[0].split('.')
                hour, minute = r[2].split(':')
                if int(month) == 1 and departure_date.month == 12:
                    year = departure_date.year + 1
                else:
                    year = departure_date.year

                time = dt.datetime(
                    year=year,
                    month=int(month),
                    day=int(day),
                    hour=int(hour),
                    minute=int(minute))
                stop_times.append(time)
        return sorted(stop_times)

    def parse_ticket(self, text):
        departure_date = self.extract_date(text)
        if not departure_date:
            raise ValueError('Departure Date could not be extracted')
        stops = self.extract_stops(text, departure_date)
        stop_times = self.extract_stop_times(text, stops, departure_date)
        return RailwayTicket(stops=stops, stop_times=stop_times)

    def parse_tickets(self, path):
        text = self.extract_text(path)
        split_pattern = 'Ihre Reiseverbindung und Reservierung R.?ckfahrt am'

        indexes = [m.start(0) for m in re.finditer(split_pattern, text)]
        if len(indexes) > 0:
            ticket_texts = [text[:indexes[0]], text[indexes[0]:]]
        else:
            ticket_texts = [text]

        return [self.parse_ticket(text) for text in ticket_texts]


class Railway(Memacs):
    available_parsers = {'DB': DBTicketParser}

    def _parser_add_arguments(self):
        """
        overwritten method of class Memacs

        add additional arguments
        """
        Memacs._parser_add_arguments(self)

        self._parser.add_argument(
          "-f", "--folder", dest="ticket_folder",
          action="append",
          help="path to a folder to search for tickets" +\
                                       "multiple folders can be specified: " + \
                                       "-f /path1 -f /path2")
        self._parser.add_argument(
            "-C", "--Company", dest="company", help="Railway Company [DB]")

    def _parser_parse_args(self):
        """
        overwritten method of class Memacs

        all additional arguments are parsed in here
        """
        Memacs._parser_parse_args(self)

        if self._args.ticket_folder:
            for f in self._args.ticket_folder:
                if not os.path.isdir(f):
                    self._parser.error("Check the folderlist argument: " +\
                                       "[" + str(f) + "] and probably more aren't folders")
        else:
            self._parser.error("You have to provide the path to a directory")

        if self._args.company:
            if self._args.company not in self.available_parsers:
                self._parser.error(
                    "There is no parser yet defined for {}".format(
                        self._args.company))
            else:
                self.parser = self.available_parsers[self._args.company]()

        else:
            self.parser.error("You have to provide the company")

    def __handle_file(self, path):
        try:
            tickets = self.parser.parse_tickets(path)
        except ValueError as e:
            return None
        for ticket in tickets:
            timestamp = OrgFormat.datetime(ticket.stop_times[0])
            end_timestamp = OrgFormat.datetime(ticket.stop_times[-1])
            output = OrgFormat.link(
                link=path,
                description="Train ride from {} to {}".format(
                    ticket.stops[0], ticket.stops[-1]),
                replacespaces=False)
            properties = OrgProperties(data_for_hashing=output + timestamp)
            properties.add('ORIGIN', ticket.stops[0])
            properties.add('DESTINATION', ticket.stops[-1])
            properties.add('DEPARTURE', OrgFormat.datetime(
                ticket.stop_times[0]))
            properties.add('ARRIVAL', OrgFormat.datetime(
                ticket.stop_times[-1]))
            self._writer.write_org_subitem(
                output=output,
                timestamp=timestamp + '-' + end_timestamp,
                properties=properties)

    def _main(self):
        """
        get's automatically called from Memacs class
        """

        for folder in self._args.ticket_folder:
            for dirpath, _, filenames in os.walk(folder):
                for f in filenames:
                    if f.endswith('.pdf'):
                        abs_path = os.path.join(dirpath, f)
                        self.__handle_file(abs_path)
