from unittest import TestCase

from pangolier.metrics import Metric
from pangolier.functions import (
    function, range_function, aggregation_operator as aggr,
)


class TestFunction(TestCase):
    def test_rate(self) -> None:
        rate = range_function('rate')

        self.assertEqual(
            rate(Metric('http_requests_total'), timespan='5m').to_str(),
            'rate(http_requests_total[5m])'
        )

    def test_increase(self) -> None:
        increase = range_function('increase')

        self.assertEqual(
            increase(Metric('http_requests_total'), timespan='5m').to_str(),
            'increase(http_requests_total[5m])'
        )

    def test_rate_with_filter(self) -> None:
        rate = range_function('rate')

        self.assertEqual(
            rate(
                Metric('http_requests_total').filter(
                    job='prometheus',
                    group='canary'
                ),
                timespan='5m'
            ).to_str(),
            'rate(http_requests_total{job="prometheus", group="canary"}[5m])'
        )

    def test_sum(self) -> None:
        sum_ = aggr('sum')

        self.assertEqual(
            sum_(Metric('http_requests_total')).to_str(),
            'sum(http_requests_total)'
        )

    def test_sum_by(self) -> None:
        sum_ = aggr('sum')

        self.assertEqual(
            sum_(
                Metric('http_requests_total'),
                by=['job', 'group'],
            ).to_str(),
            'sum by(job, group)(http_requests_total)'
        )

    def test_avg_without(self) -> None:
        avg = aggr('avg')

        self.assertEqual(
            avg(
                Metric('http_requests_total'),
                without=['job', 'group'],
            ).to_str(),
            'avg without(job, group)(http_requests_total)'
        )

    def test_sum_by_rate(self) -> None:
        rate = range_function('rate')
        sum_ = aggr('sum')

        self.assertEqual(
            sum_(
                rate(
                    Metric('http_requests_total'),
                    timespan='5m'
                ),
                by=['job', 'group'],
            ).to_str(),
            'sum by(job, group)(rate(http_requests_total[5m]))'
        )

    def test_sum_by_rate_with_filter(self) -> None:
        rate = range_function('rate')
        sum_ = aggr('sum')

        self.assertEqual(
            sum_(
                rate(
                    Metric('http_requests_total').filter(
                        job='prometheus',
                    ),
                    timespan='5m'
                ),
                by=['group']
            ).to_str(),
            'sum by(group)(rate(http_requests_total{job="prometheus"}[5m]))'  # noqa
        )

    def test_histogram_quantile(self) -> None:
        histogram_quantile = function('histogram_quantile')
        rate = range_function('rate')
        sum_ = aggr('sum')

        self.assertEqual(
            histogram_quantile(
                0.9,
                sum_(
                    rate(
                        Metric('http_request_duration_seconds_bucket'),
                        timespan='5m',
                    ),
                    by=['le']
                )
            ).to_str(),
            'histogram_quantile(0.9, sum by(le)(rate(http_request_duration_seconds_bucket[5m])))'  # noqa
        )
