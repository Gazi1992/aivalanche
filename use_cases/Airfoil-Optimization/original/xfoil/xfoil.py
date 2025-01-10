"""
This file contains all code necessary for interfacing with XFOIL.

The Xfoil class circumvents blocking problems (caused by the interactive
nature of XFOIL) by using the NonBlockingStreamReader class, that runs the
blocking some_xfoil_subprocess.stdout.readline() call in a separate thread,
exchanging information with it using a queue.

This enables the Xfoil class to interact with XFOIL, and to read polars from
stdout instead of having to write a file to disk, eliminating latency there.
(Airfoil data still needs to be read from a file by XFOIL.)

Multiple XFOIL subprocesses can be run simultaneously, simply by constructing
the Xfoil class multiple times.

As such, this is probably the fastest and most versatile XFOIL automization
script out there. (I've seen a good MATLAB implementation, but it still relied
on files for output, and was not interactive.)
"""

from __future__ import division
from time import sleep
import subprocess as subp
import numpy as np
import os
import re

from threading import Thread
from queue import Queue, Empty

def oper_visc_alpha(*args, **kwargs):
    """Wrapper for _oper_visc"""
    return _oper_visc(["ALFA","ASEQ"], *args, **kwargs)

def oper_visc_cl(*args, **kwargs):
    """Wrapper for _oper_visc"""
    return _oper_visc(["Cl","CSEQ"],*args, **kwargs)


def _oper_visc(pcmd, airfoil, operating_point, Re, Mach=None,
             normalize=True, show_seconds=None, iterlim=None, gen_naca=False):
    """
    This function automates XFOIL operations by sending commands to XFOIL as if a user
    was typing them interactively. It performs viscous analysis on an airfoil.
    
    Parameters:
    - pcmd: List of commands ["Cl","CSEQ"] or ["ALFA","ASEQ"] depending on whether we're
           analyzing at specific lift coefficients or angles of attack
    - airfoil: Path to airfoil data file or NACA designation
    - operating_point: Either a single value or [start, stop, step] for sequence analysis
    - Re: Reynolds number for the analysis
    - Mach: Optional Mach number for compressibility effects
    - normalize: Whether to normalize the airfoil coordinates
    - show_seconds: How long to show XFOIL plots (if enabled)
    - iterlim: Maximum number of iterations for convergence
    - gen_naca: Whether to generate a NACA airfoil instead of loading from file
    """
    # Get the directory where this script is located
    # This helps with relative file paths
    path = os.path.dirname(os.path.realpath(__file__))
    
    # Create a new instance of XFOIL subprocess
    xf = Xfoil(path)

    # If normalize=True, normalize the airfoil coordinates 
    # This ensures consistent coordinate scaling
    if normalize:
        xf.cmd("NORM")

    # Either generate a NACA airfoil or load one from file
    if gen_naca:
        # For NACA airfoils, just send the NACA number (e.g., "NACA 2412")
        xf.cmd(airfoil)
    else:
        # For file input, use LOAD command with double newline to handle prompts
        xf.cmd('LOAD {}\n\n'.format(airfoil),
               autonewline=False)

    # Disable graphics plotting to speed up operation
    # PLOP enters plotting options menu, G toggles graphics, double newline exits
    if not show_seconds:
        xf.cmd("PLOP\nG\n\n", autonewline=False)

    # Enter XFOIL's OPER (operation) menu where analysis commands are available
    xf.cmd("OPER")

    # Set iteration limit if specified (default is 10 in XFOIL)
    if iterlim:
        xf.cmd("ITER {:.0f}".format(iterlim))

    # Turn on viscous mode with specified Reynolds number
    xf.cmd("VISC {}".format(Re))

    # Set Mach number if specified (for compressible flow analysis)
    if Mach:
        xf.cmd("MACH {:.3f}".format(Mach))

    # Enable polar accumulation (saving of results)
    # Triple newline: first for PACC command, next two to skip saving polar and dump files
    xf.cmd("PACC\n\n\n", autonewline=False)

    # Set up the analysis sequence
    try:
        # Check if operating_point is a sequence [start, stop, step]
        if len(operating_point) != 3:
            raise Warning("oper pt is single value or [start, stop, interval]")
        
        # Use sequence command (ASEQ for alpha sequence, CSEQ for Cl sequence)
        # *operating_point unpacks the three values into the format string
        xf.cmd("{:s} {:.3f} {:.3f} {:.3f}".format(pcmd[1], *operating_point))
        # '!' tells XFOIL to start the sequence
        xf.cmd("!")
    except TypeError:
        # If operating_point is a single value, use single-point analysis
        # (ALFA for angle of attack, Cl for lift coefficient)
        xf.cmd("{:s} {:.3f}".format(pcmd[0], operating_point))

    # Get the analysis results
    # PLIS command lists the accumulated polar
    # ENDD is a marker we add to know when output is complete
    xf.cmd("PLIS\nENDD\n\n", autonewline=False)
    
    print("Xfoil module starting read")
    # Collect all output until we see our ENDD marker
    output = ['']
    while not re.search("ENDD", output[-1]):
        line = xf.readline()
        if line:
            print(line)
            output.append(line)
    print("Xfoil module ending read")

    # If show_seconds is set, pause to show plots
    if show_seconds:
        sleep(show_seconds)

    # Parse the output into a usable format (converts XFOIL's text output into arrays)
    return parse_stdout_polar(output)


def parse_stdout_polar(lines):
    """Converts polar 'PLIS' data to array"""    
    def clean_split(s): return re.split('\s+', s.replace(os.linesep,''))[1:]

    # Find location of data from ---- divider
    for i, line in enumerate(lines):
        if re.match('\s*---', line):
            dividerIndex = i
    
    # What columns mean
    data_header = clean_split(lines[dividerIndex-1])

    # Clean info lines
    info = ''.join(lines[dividerIndex-4:dividerIndex-2])
    info = re.sub("[\r\n\s]","", info)
    # Parse info with regular expressions
    def p(s): return float(re.search(s, info).group(1))
    infodict = {
     'xtrf_top': p("xtrf=(\d+\.\d+)"),
     'xtrf_bottom': p("\(top\)(\d+\.\d+)\(bottom\)"),
     'Mach': p("Mach=(\d+\.\d+)"),
     'Ncrit': p("Ncrit=(\d+\.\d+)"),
     'Re': p("Re=(\d+\.\d+e\d+)")
    }

    # Extract, clean, convert to array
    datalines = lines[dividerIndex+1:-2]
    data_array = np.array(
    [clean_split(dataline) for dataline in datalines], dtype='float')

    return data_array, data_header, infodict


class Xfoil():
    """
    This class basically represents an XFOIL child process, and should
    therefore not implement any convenience functions, only direct actions
    on the XFOIL process.
    """
    
    def __init__(self, path=""):
        """Spawn xfoil child process"""
        # Use system xfoil instead of looking for it in the project directory
        self.xfinst = subp.Popen("xfoil",
                  stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.PIPE)
        self._stdoutnonblock = NonBlockingStreamReader(self.xfinst.stdout)
        self._stdin = self.xfinst.stdin
        self._stderr = self.xfinst.stderr

    def cmd(self, cmd, autonewline=True):
        """Give a command. Set newline=False for manual control with '\n'"""
        n = '\n' if autonewline else ''
        # Convert string to bytes for Python 3
        self.xfinst.stdin.write((cmd + n).encode('utf-8'))
        self.xfinst.stdin.flush()  # Make sure the command is sent

    def readline(self):
        """Read one line, returns None if empty"""
        line = self._stdoutnonblock.readline()
        return line.decode('utf-8') if line else None

    def close(self):
        self.xfinst.kill()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

class UnexpectedEndOfStream(Exception): pass

class NonBlockingStreamReader:
    """XFOIL is interactive, thus readline() blocks. The solution is to
       let another thread handle the XFOIL communication, and communicate
       with that thread using a queue.
       From http://eyalarubas.com/python-subproc-nonblock.html"""
 
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''
        self._s = stream
        self._q = Queue()
        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    #print "NonBlockingStreamReader: End of stream"
                    # Make sure to terminate
                    return
                    #raise UnexpectedEndOfStream
        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        # Start collecting lines from the stream
        self._t.start()

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None


if __name__ == "__main__":
    print (oper_visc_alpha("NACA 2215", [0,5,1], 2E6, Mach=.6,
                          gen_naca=True, show_seconds=2))