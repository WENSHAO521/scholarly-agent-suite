"""Implements the voice-precedence and confidence-gating logic described in
references/corpus-profile-integration.md:

    user author profile
      -> discipline conventions
        -> target journal observed profile
          -> selected historical/abstract voice profile

A low-confidence journal or historical contribution should only weakly
influence the result — this resolves a disagreement by precedence-with-
confidence-gating, never by numeric averaging (see that file's
§Conflict resolution).
"""
from __future__ import annotations

PRECEDENCE = ("author", "discipline", "journal", "historical")

# Only journal/historical layers are corpus-derived and confidence-rated in
# practice (author and discipline conventions are treated as authoritative
# inputs, not sampled estimates) — see corpus-profile-integration.md.
CONFIDENCE_GATED_LAYERS = ("journal", "historical")


def resolve_voice_precedence(layers: dict, confidence: dict | None = None):
    """Resolve a per-field voice value across up to four layers.

    Args:
        layers: mapping of layer name ("author", "discipline", "journal",
            "historical") to a dict of field -> value. Missing layers or
            missing fields within a layer are fine.
        confidence: optional mapping of layer name -> "high"|"medium"|"low",
            applied only to CONFIDENCE_GATED_LAYERS. A "low" confidence
            contribution is skipped in favor of a lower-precedence layer's
            value for that field, unless it's the only layer defining the
            field at all.

    Returns:
        (resolved, conflicts) where `resolved` is a dict of field -> chosen
        value, and `conflicts` lists every field where more than one layer
        proposed a value, recording which layer won and what was overridden
        (useful for surfacing a "journal-conflict" style resolution to the
        user rather than silently picking one).
    """
    confidence = confidence or {}
    fields: set[str] = set()
    for layer_values in layers.values():
        fields.update(layer_values.keys())

    resolved: dict = {}
    conflicts: list[dict] = []

    for field_name in sorted(fields):
        contributions = []
        for layer in PRECEDENCE:
            layer_values = layers.get(layer, {})
            if field_name in layer_values and layer_values[field_name] is not None:
                contributions.append((layer, layer_values[field_name]))

        if not contributions:
            continue

        eligible = [
            (layer, value)
            for layer, value in contributions
            if not (layer in CONFIDENCE_GATED_LAYERS and confidence.get(layer) == "low")
        ]
        # If confidence-gating would eliminate every contribution, fall back
        # to the full list rather than dropping the field entirely.
        chosen_layer, chosen_value = (eligible or contributions)[0]
        resolved[field_name] = chosen_value

        if len(contributions) > 1:
            conflicts.append(
                {
                    "field": field_name,
                    "chosen_layer": chosen_layer,
                    "chosen_value": chosen_value,
                    "overridden": [
                        {"layer": layer, "value": value}
                        for layer, value in contributions
                        if layer != chosen_layer
                    ],
                }
            )

    return resolved, conflicts
