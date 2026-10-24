import unittest
from metric_visuals import sparkline_svg, metric_panel, journal_chips
from open_metrics import METRIC, H_INDEX


class MetricVisualTests(unittest.TestCase):
    def test_five_years_are_ordered_even_when_source_is_not(self):
        svg = sparkline_svg([{'year': 2025, 'citations': 20}, {'year': 2021, 'citations': 5}])
        self.assertLess(svg.index('2021: 5'), svg.index('2025: 20'))
        self.assertIn('2023: sem registro', svg)

    def test_zero_is_plotted_and_missing_does_not_become_zero(self):
        svg = sparkline_svg([{'year': 2021, 'citations': 0}, {'year': 2023, 'citations': 4}])
        self.assertIn('2021: 0 citações', svg)
        self.assertEqual(svg.count('<circle '), 2)
        self.assertNotIn('2022: 0 citações', svg)

    def test_missing_history_does_not_fabricate_line(self):
        self.assertNotIn('<svg', sparkline_svg([]))

    def test_metric_values_are_complete_and_labeled(self):
        html = metric_panel({METRIC: 27.8, H_INDEX: 3400})
        self.assertIn('27,80', html)
        self.assertIn('3.400', html)
        self.assertIn('OpenAlex', html)
        self.assertNotIn('JIF', html)

    def test_dynamic_labels_are_escaped(self):
        html = journal_chips('<script>bad</script>', 'Publisher', True)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)


if __name__ == '__main__':
    unittest.main()
