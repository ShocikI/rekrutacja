from django.test import TestCase, Client
from django.urls import resolve, reverse
from unittest.mock import patch
from .views import get_events, get_month_name, start, calendar_view, day_view, get_date_data, get_event_by_id
from rekrutacja.settings import API_KEY, BASE_URL

class UnitTests(TestCase):
    # url test
    # Sprawdzamy czy przy użyciu ścieżki startowej wyświetla się startowa strona
    def test_url_start(self):
        url = reverse("start")
        self.assertEqual(resolve(url).func, start)

    # Sprawdzamy czy przy użyciu ścieżki do danego miesiąca wyświetlony zostanie dany miesiąc
    def test_url_calendar_view(self):
        url = reverse("calendar_view", kwargs={'year':2022, 'month':10})
        self.assertEqual(resolve(url).func, calendar_view)

    # Sprawdzamy czy przy użyciu ścieżki do danego dnia wyświetlony zostanie dany dzień
    def test_url_day_view(self):
        url = reverse('day_view', kwargs={'year':2022, "month":10, "day":22})
        self.assertEqual(resolve(url).func, day_view)
    
    # test functions
    # Sprawdzamy czy uzyskamy odpowiednią nazwę miesiąca
    def test_get_month_name(self):
        self.assertEqual(get_month_name(2), "Luty")
        self.assertEqual(get_month_name(5), "Maj")
        self.assertEqual(get_month_name(11), "Listopad")

    # Sprawdzamy czy uzyskamy odpowiednie dane do kalendarza
    def test_get_date_data_basic(self):
        data = get_date_data(2022, 5)
        self.assertEqual(data, ("Maj", 4, 2022, 6, 2022))
        data = get_date_data(2022, 1)
        self.assertEqual(data, ("Styczeń", 12, 2021, 2, 2022))
        data = get_date_data(2022, 12)
        self.assertEqual(data, ('Grudzień', 11, 2022, 1, 2023))
        data = get_date_data(2022, 15)
    
    # Sprawdzamy czy uzyskamy odpowiednie dane do kalendarza przy liczbie reporezentującej miesiąc wykraczającej poza zakres 1-12
    def test_det_date_data_overlap(self):
        data = get_date_data(2022, -17) # -17 % 12 = 7
        self.assertEqual(data, ("Lipiec", 6, 2021, 8, 2021))
        data = get_date_data(2022, 18) # 18 % 12 = 6
        self.assertEqual(data, ("Czerwiec", 5, 2023, 7, 2023))

    # Test łączenia z API
    @patch("calendar_events.views.requests.get")
    def test_get_events_success(self, mock_get):
        mock_get.return_value.status_code = 200

        response = get_events()
        mock_get.return_value.json.return_value = {'key': 'value'}

        self.assertIsNotNone(response)
        mock_get.assert_called_once_with(
            f"{BASE_URL}/events",
            headers={'api-key': f"{API_KEY}"}
        )
    
    @patch("calendar_events.views.requests.get")
    def test_get_events_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = None

        response = get_events()

        self.assertIsNone(response)
        mock_get.assert_called_once_with(
            f"{BASE_URL}/events",
            headers={'api-key': f"{API_KEY}"}
        )

    @patch("calendar_events.views.requests.get")
    def test_get_events_by_id_success(self, mock_get):
        mock_get.return_value.status_code = 200
        event_id = 3
        response = get_event_by_id(event_id)
        mock_get.return_value.json.return_value = {'key': 'value'}

        self.assertIsNotNone(response)
        mock_get.assert_called_once_with(
            f"{BASE_URL}/events/{event_id}",
            headers={'api-key': f"{API_KEY}"}
        )
    
    @patch("calendar_events.views.requests.get")
    def test_get_events_by_id_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = None
        event_id = 3
        response = get_event_by_id(event_id)

        self.assertIsNone(response)
        mock_get.assert_called_once_with(
            f"{BASE_URL}/events/{event_id}",
            headers={'api-key': f"{API_KEY}"}
        )

    @patch("calendar_events.views.requests.get")
    def test_get_event_by_non_existing_id(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = None
        event_id = "aaa"
        response = get_event_by_id(event_id)

        self.assertIsNone(response)
        mock_get.assert_called_once_with(
            f"{BASE_URL}/events/{event_id}",
            headers={'api-key': f"{API_KEY}"}
        )