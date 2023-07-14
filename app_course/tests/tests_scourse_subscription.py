from rest_framework import status

from app_course.tests.tests_course import BaseTestCase


class CourseSubscriptionTestCase(BaseTestCase):
    def setUp(self):
        """
        Создание курсов.
        """
        super().setUp()
        self.created_courses = []
        self.created_course_ids = []

        for course in self.course_data:
            response = self.user_clients[0].post('/api/courses/', course)
            self.created_courses.append(response.json())

        for i, course in enumerate(self.created_courses):
            course_id = self.created_courses[i]['id']
            self.created_course_ids.append(course_id)

    def test_new_course_has_subscribed_false(self):
        """
        Новый курс имеет флаг подписки False
        """
        courses_response = self.user_clients[0].get('/api/courses/')
        courses = courses_response.json()['results']
        for course in courses:
            self.assertFalse(course['subscribed'])

    def test_enable_course_subscribed(self):
        """
        Подписка на курс. Флаг подписки True
        """
        for course_id in self.created_course_ids:
            response = self.user_clients[0].post('/api/course-subscriptions/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            courses_response = self.user_clients[0].get(f'/api/courses/{course_id}/')
            course = courses_response.json()
            self.assertTrue(course['subscribed'])

    def test_cannot_subscribe_twice(self):
        """
        Проверка, что повторная подписка на курс, на который пользователь уже подписан, невозможна
        """
        for course_id in self.created_course_ids:
            response = self.user_clients[0].post('/api/course-subscriptions/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.user_clients[0].post('/api/course-subscriptions/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_course(self):
        """
        Отписка от курса. Флаг подписки False
        """
        for course_id in self.created_course_ids:
            response = self.user_clients[0].post('/api/course-subscriptions/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.user_clients[0].put('/api/course-unsubscribe/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            courses_response = self.user_clients[0].get('/api/courses/')
            courses = courses_response.json()['results']
            for course in courses:
                if course['id'] == course_id:
                    self.assertFalse(course['subscribed'])

    def test_cannot_unsubscribe_twice(self):
        """
        Проверка, что повторная отписка от курса, от которого пользователь уже отписан невозможна.
        """
        for course_id in self.created_course_ids:
            response = self.user_clients[0].post('/api/course-subscriptions/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.user_clients[0].put('/api/course-unsubscribe/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.user_clients[0].put('/api/course-unsubscribe/', {'course': course_id})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_to_non_existent_course(self):
        """
        Проверка, что при попытке подписаться на несуществующий курс будет возвращен статус 400
        :return:
        """
        response = self.user_clients[0].post('/api/course-subscriptions/', {'course': 999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_to_non_existent_course(self):
        """
        Проверка, что при попытке отписаться от несуществующего курса будет возвращен статус 400
        :return:
        """
        response = self.user_clients[0].put('/api/course-unsubscribe/', {'course': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
