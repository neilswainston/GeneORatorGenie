'''
DNA++ (c) DNA++ 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
import datetime
import sys

from Bio.Seq import Seq
from synbiochem.utils import seq_utils


_DEFAULT_CODONS = {am_ac: 'NNK' for am_ac in seq_utils.AA_CODES.values()}


def get_oligos(templ, flank_seqs=None, set_len=1, melt_temp=60, codons=None):
    '''Gets oligos.'''
    if flank_seqs is None:
        flank_seqs = {'pre': '', 'post': ''}

    oligos = []
    def_codons = _get_codons(codons)
    seq = ''.join([flank_seqs['pre'], templ, flank_seqs['post']])
    offset = len(flank_seqs['pre'])

    for set_idx, _ in enumerate(xrange(0, len(templ), 3 * set_len)):
        oligos.extend(_get_set(seq, offset, offset + len(templ), set_idx,
                               set_len, melt_temp, def_codons))

    return oligos


def _get_codons(codons):
    '''Gets codons.'''
    if codons is None:
        codons = {}

    def_codons = dict(_DEFAULT_CODONS)
    def_codons.update(codons)
    return def_codons


def _get_set(seq, offset, templ_end, set_idx, set_len, melt_temp, def_codons):
    '''Gets a set.'''
    oligos = []

    start_pos = offset + (set_idx * set_len * 3)
    end_pos = start_pos + 3 * set_len
    pre_seq, pre_tm = _get_seq_by_tm(seq[:start_pos], melt_temp, False,
                                     terminii=['C', 'G'])
    post_seq, post_tm = _get_seq_by_tm(seq[end_pos:], melt_temp,
                                       terminii=['C', 'G'])

    for set_member in range(min(set_len, len(seq[start_pos:templ_end]) / 3)):
        oligo = _get_oligo(seq, offset, set_idx, set_member, set_len,
                           pre_seq, post_seq, def_codons)

        oligo.extend([pre_tm, post_tm,
                      str(datetime.date.today()) +
                      '_' + str(set_idx + 1) +
                      '.' + str(set_member + 1)])
        oligos.append(oligo)

    return oligos


def _get_oligo(seq, offset, set_idx, set_member, set_len, pre_seq, post_seq,
               def_codons):
    '''Gets oligo.'''
    start_pos = offset + (set_idx * set_len * 3)
    end_pos = start_pos + 3 * set_len

    pos = start_pos + 3 * set_member
    codon = Seq(seq[pos:pos + 3])

    seq = pre_seq + \
        seq[start_pos:pos] + \
        def_codons[str(codon.translate())] + \
        seq[pos + 3: end_pos] + \
        post_seq

    return [set_idx + 1,
            set_member + 1,
            seq,
            len(seq)]


def _get_seq_by_tm(seq, melt_temp, forward=True, terminii=None):
    '''Gets sequence by melting temp.'''
    if terminii is None:
        terminii = ['A', 'C', 'G', 'T']

    t_m = seq_utils.get_melting_temp(seq) if seq else float('NaN')

    try:
        seq, t_m = seq_utils.get_seq_by_melt_temp(seq, melt_temp, forward,
                                                  terminii, tol=0.075)
    except ValueError:
        pass

    return seq, t_m


def main(args):
    '''main method.'''
    print '\t'.join(['Residue',
                     'Set number',
                     'Set member',
                     'Sequence',
                     'Length',
                     '5\' Tm',
                     '3\' Tm',
                     'id'])
    for idx, oligo in enumerate(get_oligos(args[0].upper(),
                                           {'pre': args[1].upper(),
                                            'post': args[2].upper()},
                                           set_len=int(args[3]),
                                           melt_temp=float(args[4]),
                                           codons={'S': 'NNK'})):
        print '\t'.join(str(val) for val in [idx + 1] + oligo)


if __name__ == '__main__':
    main(sys.argv[1:])
