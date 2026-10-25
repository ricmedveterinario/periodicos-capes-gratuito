"""Public API for local manuscript recommendations; no external services."""
from catalog_rules import integral_candidate, institution_publishers
from text_normalization import clean, tokens
from legacy_recommender import JournalRecommender as LegacyJournalRecommender
from modular_recommender import ModularJournalRecommender as JournalRecommender
