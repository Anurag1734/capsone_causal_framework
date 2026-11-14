# BETA-VAE PROVENANCE REPORT

## Decision

The beta-VAE latent dimensions are not eligible for primary causal analysis in the current workspace because the provenance chain cannot be audited from the available artifacts.

## Required provenance checks

1. Training checkpoint identity.
2. Training cohort and split definitions.
3. Whether acute MI ECGs were included in unsupervised training.
4. Embedding extraction procedure and deterministic behavior.
5. Patient and ECG mapping integrity.
6. Missingness and latent variance diagnostics.

## Current workspace status

The repository does not contain the model weights, training metadata, or latent extraction outputs required to complete these checks. The absence of `data/modeling/ecg_embeddings` and the lack of a corresponding training checkpoint make this an unresolvable provenance gap.

## Conclusion

The 64-dimensional latent vectors should remain excluded from the primary causal analysis until provenance is independently reconstructed and validated.
