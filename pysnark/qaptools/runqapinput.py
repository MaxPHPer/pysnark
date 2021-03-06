# Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
# copyright license for redistribution and use in source and binary forms,
# with or without modification, is hereby granted for non-commercial,
# experimental and research purposes, provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the
#   documentation and/or other materials provided with the distribution. If
#   you wish to use this software commercially, kindly contact
#   info.licensing@philips.com to obtain a commercial license.
#
# This license extends only to copyright and does not include or grant any
# patent license or other license whatsoever.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import random
import subprocess
import sys

import pysnark.options
import runqapgen


def run(bname):
    """
    Run the qapinput tool to build a commitment file representing some data.
    The input file (given by :py:func:`pysnark.options.get_block_file`) consists
    of one value per line, plus a last line of randomness. The output file
    generated is given by :py:func:`pysnark.options.get_block_comm`.

    :param bname: Block name
    :return: None
    """

    bfile = pysnark.options.get_block_file(bname)
    bcomm = pysnark.options.get_block_comm(bname)

    mpkey = pysnark.options.get_mpkey_file()
    print >>sys.stderr, "Building block commitment", bcomm, "from wires", bfile

    blockcomm = open(bcomm, "w")
    ret = subprocess.call([pysnark.options.get_qaptool_exe("qapinput"), mpkey, bfile], stdout=blockcomm)
    blockcomm.close()
    if ret != 0:
        sys.exit(2)


def writecomm(blocknm, vals, rnd=None):
    """
    Write values to a commitment file

    :param bfile: Block name
    :param data: List of integer values to commit to
    :param rnd: Randomness for the commitment (or generate if not given)
    :return: None
    """

    blockfile = open(pysnark.options.get_block_file(blocknm), "w")
    for val in vals: print >>blockfile, val
    print >>blockfile, rnd if rnd is not None else random.SystemRandom().randint(0, pysnark.options.vc_p-1)
    blockfile.close()


def gencomm(blocknm, vals, rnd=None):
    """
    Generate commitment file and commitment

    :param blocknm: Block name
    :param vals: List of integer values to commit to
    :param rnd: Randomness for the commitment (or generate if not given)
    :return: None
    """

    writecomm(blocknm, vals, rnd)
    runqapgen.ensure_mkey(-1, len(vals))
    run(blocknm)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print >>sys.stderr, "*** Usage:", sys.argv[0], "<bname> [values]"
        sys.exit(2)

    vals = []

    if len(sys.argv) == 2:
        for ln in sys.stdin:
            vals.extend(map(int, ln.strip().split()))
    else:
        vals.extend(map(int, sys.argv[2:]))

    gencomm(sys.argv[1], vals)
