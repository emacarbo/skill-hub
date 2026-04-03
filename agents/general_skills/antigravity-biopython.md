---
name: biopython
description: "Python tools for computational molecular biology -- sequences, alignments, BLAST, structures, and phylogenetics."
---

# Biopython

Comprehensive Python toolkit for biological computation: sequence manipulation, file I/O (FASTA, GenBank, PDB), NCBI database access, BLAST searches, structural bioinformatics, and phylogenetics. Current version: 1.85 (requires Python 3, NumPy).

## Key Patterns

- **SeqIO for file I/O**: `SeqIO.parse("file.fasta", "fasta")` reads sequences; supports FASTA, GenBank, FASTQ, and 20+ formats
- **Set Entrez email**: `Entrez.email = "you@example.com"` is mandatory for NCBI database access; add `api_key` for 10 req/s
- **Use iterators for large files**: `for record in SeqIO.parse(...)` processes one record at a time, avoids memory issues
- **Sequence operations**: `seq.translate()`, `seq.reverse_complement()`, `seq.transcribe()` on `Seq` objects
- **BLAST**: `NCBIWWW.qblast("blastn", "nt", sequence)` for remote; use local BLAST for large-scale searches
- **PDB structures**: `PDBParser(QUIET=True).get_structure("id", "file.pdb")` -- navigate Structure/Model/Chain/Residue/Atom hierarchy
- **Pairwise alignment**: `Align.PairwiseAligner()` with `mode='global'` or `'local'`
- **Phylogenetics**: `Phylo.read("tree.nwk", "newick")` for tree I/O; build trees from distance matrices
- **Format conversion**: `SeqIO.convert("input.gb", "genbank", "output.fasta", "fasta")`
- **Sequence stats**: `gc_fraction(seq)`, `molecular_weight(seq)`, melting temperature via `Bio.SeqUtils`

## Quick Reference

### Module Map

| Module | Purpose |
|:-------|:--------|
| `Bio.Seq` / `Bio.SeqIO` | Sequence objects and file I/O |
| `Bio.Align` / `Bio.AlignIO` | Pairwise and multiple sequence alignments |
| `Bio.Entrez` | NCBI database access (GenBank, PubMed, Protein) |
| `Bio.Blast` | BLAST searches (remote and local) |
| `Bio.PDB` | 3D protein structure parsing and analysis |
| `Bio.Phylo` | Phylogenetic tree I/O and visualization |
| `Bio.SeqUtils` | GC content, molecular weight, melting temp |
| `Bio.motifs` | Sequence motif finding and analysis |
| `Bio.Restriction` | Restriction enzyme site analysis |

### Core Code Patterns

```python
from Bio import SeqIO, Entrez, Phylo
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

# Read FASTA
for rec in SeqIO.parse("seqs.fasta", "fasta"):
    print(f"{rec.id}: {len(rec.seq)} bp, GC={gc_fraction(rec.seq):.2%}")

# Convert formats
SeqIO.convert("input.gb", "genbank", "output.fasta", "fasta")

# Fetch from NCBI
Entrez.email = "you@example.com"
handle = Entrez.efetch(db="nucleotide", id="EU490707", rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
handle.close()

# Sequence operations
seq = Seq("ATCGATCG")
protein = seq.translate()
rc = seq.reverse_complement()

# BLAST search
from Bio.Blast import NCBIWWW, NCBIXML
result = NCBIWWW.qblast("blastn", "nt", str(seq))
blast_record = NCBIXML.read(result)
for aln in blast_record.alignments[:5]:
    print(f"{aln.title}: E={aln.hsps[0].expect}")

# PDB structure
from Bio.PDB import PDBParser
structure = PDBParser(QUIET=True).get_structure("1crn", "1crn.pdb")
dist = structure[0]["A"][10]["CA"] - structure[0]["A"][20]["CA"]

# Phylogenetic tree
tree = Phylo.read("tree.nwk", "newick")
Phylo.draw_ascii(tree)

# Pairwise alignment
from Bio import Align
aligner = Align.PairwiseAligner()
aligner.mode = 'global'
alignments = aligner.align("ACCGGT", "ACGGT")
```

### Common Pitfalls

- Forgetting `Entrez.email` -- NCBI will block requests
- Using `SeqIO.read()` for multi-record files -- use `SeqIO.parse()` instead
- Loading entire large FASTA into memory -- iterate with `SeqIO.parse()`
- Mismatched format string -- "fasta" not "FASTA", "genbank" not "gb"

## When to Use

- Reading, writing, or converting biological sequence files (FASTA, GenBank, FASTQ)
- Searching NCBI databases or running BLAST queries programmatically
- Analyzing protein 3D structures from PDB/mmCIF files
- Building phylogenetic trees from alignments or distance matrices
- Calculating sequence statistics (GC content, molecular weight, restriction sites)

## Resources

- [Biopython Tutorial](https://biopython.org/docs/latest/Tutorial/)
- [GitHub](https://github.com/biopython/biopython)
