from pynag.Parsers import StatusDat

class StatusDat(StatusDat):

    def parse(self):
        """ Parses your status.dat file and stores in a dictionary under self.data

        Returns:

            None

        Raises:

            :py:class:`ParserError`: if problem arises while reading status.dat

            :py:class:`ParserError`: if status.dat is not found

            :py:class:`IOError`: if status.dat cannot be read
        """
        self.data = {}
        status = None  # Holds all attributes of a single item
        key = None  # if within definition, store everything before =
        value = None  # if within definition, store everything after =
        if not self.filename:
            raise ParserError("status.dat file not found")
        lines = open(self.filename, 'rb').readlines()
        for sequence_no, line in enumerate(lines):
            line_num = sequence_no + 1
            # Cleanup and line skips
            line = line.strip()
            if line == "":
                pass
            elif line[0] == "#" or line[0] == ';':
                pass
            elif line.find("{") != -1 and status is None:
                status = {}
                status['meta'] = {}
                status['meta']['type'] = line.split("{")[0].strip()
            elif line[0] == "}": #.find("}") != -1:
                # Status definition has finished, lets add it to
                # self.data
                if status['meta']['type'] not in self.data:
                    self.data[status['meta']['type']] = []
                self.data[status['meta']['type']].append(status)
                status = None
            else:
                tmp = line.split("=", 1)
                if len(tmp) == 2:
                    (key, value) = line.split("=", 1)
                    status[key] = value
                elif key == "long_plugin_output":
                    # special hack for long_output support. We get here if:
                    # * line does not contain {
                    # * line does not contain }
                    # * line does not contain =
                    # * last line parsed started with long_plugin_output=
                    status[key] += "\n" + line
                else:
                    raise ParserError("Error on %s:%s: Could not parse line: %s" % (self.filename, line_num, line))
