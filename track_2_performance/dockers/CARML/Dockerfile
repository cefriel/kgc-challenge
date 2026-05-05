################################################################################
# CARML
# https://github.com/carml/carml
#
# Reactive RML engine with two evaluator backends:
#   - in-process DuckDB-based evaluator (default; primary submission)
#   - fully reactive evaluator (selectable via -E reactive)
#
# This Dockerfile pulls the published image for the KGCW 2026 Track 2 submission.
# The image was built from carml/carml @ rml-cg branch, commit 384b18f1, and
# carml/carml-jar @ rml-cg branch, commit c91e45e.
#
# Build:
#   docker build -t carml:latest .
#
# To pin to a different revision, pass the IMAGE arg:
#   docker build --build-arg IMAGE=pmaria/carml:rml-cg-<rev> -t carml:latest .
################################################################################

ARG IMAGE=pmaria/carml:rml-cg-384b18f1
FROM ${IMAGE}
