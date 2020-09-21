"""Tests Figures learner-metrics viewset
"""

import pytest

import django.contrib.sites.shortcuts
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from figures.sites import get_user_ids_for_site
from figures.views import LearnerMetricsViewSet

from tests.helpers import OPENEDX_RELEASE, GINKGO, organizations_support_sites
from tests.views.base import BaseViewTest
from tests.views.helpers import is_response_paginated, make_caller


def filter_enrollments(enrollments, courses):
    course_ids = [elem.id for elem in courses]
    return [elem for elem in enrollments if elem.course_id in course_ids]


@pytest.mark.django_db
class TestLearnerMetricsViewSet(BaseViewTest):
    """Tests the learner metrics viewset

    The tests are incomplete

    The list action will return a list of the following records:

    ```
        {
            "id": 109,
            "username": "chasecynthia",
            "email": "msnyder@gmail.com",
            "fullname": "Brandon Meyers",
            "is_active": true,
            "date_joined": "2020-06-03T00:00:00Z",
            "enrollments": [
                {
                    "id": 9,
                    "course_id": "course-v1:StarFleetAcademy+SFA01+2161",
                    "date_enrolled": "2020-02-24",
                    "is_enrolled": true,
                    "progress_percent": 1.0,
                    "progress_details": {
                        "sections_worked": 20,
                        "points_possible": 100.0,
                        "sections_possible": 20,
                        "points_earned": 50.0
                    }
                }
            ]
        }
    ```
    """
    base_request_path = 'api/learner-metrics/'
    view_class = LearnerMetricsViewSet

    @pytest.fixture(autouse=True)
    def setup(self, db, settings):
        if organizations_support_sites():
            settings.FEATURES['FIGURES_IS_MULTISITE'] = True
        super(TestLearnerMetricsViewSet, self).setup(db)

    def make_request(self, monkeypatch, request_path, site, caller, action):
        """Convenience method to make the API request

        Returns the response object
        """
        request = APIRequestFactory().get(request_path)
        request.META['HTTP_HOST'] = site.domain
        monkeypatch.setattr(django.contrib.sites.shortcuts,
                            'get_current_site',
                            lambda req: site)
        force_authenticate(request, user=caller)
        view = self.view_class.as_view({'get': action})
        return view(request)

    def test_list_method_all(self, monkeypatch, lm_test_data):
        """Partial test coverage to check we get all site users

        Checks returned user ids against all user ids for the site
        Checks top level keys

        Does NOT check values in the `enrollments` key. This should be done as
        follow up work
        """
        us = lm_test_data['us']
        them = lm_test_data['them']
        our_courses = us['courses']
        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        assert len(our_courses) > 1

        response = self.make_request(request_path=self.base_request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]
        user_ids = get_user_ids_for_site(site=us['site'])
        assert set(result_ids) == set(user_ids)
        # Spot check the first record
        top_keys = ['id', 'username', 'email', 'fullname', 'is_active',
                    'date_joined', 'enrollments']
        assert set(results[0].keys()) == set(top_keys)

    def test_course_param_single(self, monkeypatch, lm_test_data):
        """Test that the 'course' query parameter works

        """
        us = lm_test_data['us']
        them = lm_test_data['them']
        our_enrollments = us['enrollments']
        our_courses = us['courses']

        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        assert len(our_courses) > 1
        query_params = '?course={}'.format(str(our_courses[0].id))

        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')

        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]

        course_enrollments = [elem for elem in our_enrollments
                              if elem.course_id == our_courses[0].id]
        expected_user_ids = [obj.user.id for obj in course_enrollments]
        assert set(result_ids) == set(expected_user_ids)

    def test_course_param_multiple(self, monkeypatch, lm_test_data):
        """Test that the 'course' query parameter works

        """
        us = lm_test_data['us']
        them = lm_test_data['them']
        our_enrollments = us['enrollments']
        our_courses = us['courses']
        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        assert len(our_courses) > 1

        filtered_courses = our_courses[:2]

        # TODO: build params from 'filtered_courses'
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     str(our_courses[1].id))

        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')

        # Continue updating here
        assert response.status_code == status.HTTP_200_OK
        assert is_response_paginated(response.data)
        results = response.data['results']
        # Check user ids
        result_ids = [obj['id'] for obj in results]
        expected_enrollments = filter_enrollments(enrollments=our_enrollments,
                                                  courses=filtered_courses)
        expected_user_ids = [obj.user.id for obj in expected_enrollments]
        assert set(result_ids) == set(expected_user_ids)

    def invalid_course_ids_raise_404(self, monkeypatch, lm_test_data, query_params):
        us = lm_test_data['us']
        them = lm_test_data['them']

        caller = make_caller(us['org'])
        assert us['site'].domain != them['site'].domain
        request_path = self.base_request_path + query_params
        response = self.make_request(request_path=request_path,
                                     monkeypatch=monkeypatch,
                                     site=us['site'],
                                     caller=caller,
                                     action='list')
        return response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.skipif(not organizations_support_sites(),
                        reason='Organizations support sites')
    def test_valid_and_course_param_from_other_site_invalid(self,
                                                            monkeypatch,
                                                            lm_test_data):
        """Test that the 'course' query parameter works

        """
        our_courses = lm_test_data['us']['courses']
        their_courses = lm_test_data['them']['courses']
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     str(their_courses[0].id))
        assert self.invalid_course_ids_raise_404(monkeypatch,
                                                 lm_test_data,
                                                 query_params)

    def test_valid_and_mangled_course_param_invalid(self, monkeypatch, lm_test_data):
        """Test that the 'course' query parameter works

        """
        our_courses = lm_test_data['us']['courses']
        mangled_course_id = 'she-sell-seashells-by-the-seashore'
        query_params = '?course={}&course={}'.format(str(our_courses[0].id),
                                                     mangled_course_id)
        assert self.invalid_course_ids_raise_404(monkeypatch,
                                                 lm_test_data,
                                                 query_params)
