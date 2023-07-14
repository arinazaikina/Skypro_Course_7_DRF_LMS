from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app_user.models import CustomUser


class BaseTestCase(APITestCase):
    """
    Настройки базового тест-кейса.
    Создание пользователей - два обычных пользователя и модератор.
    Для каждого пользователя создается свой клиент.
    Аутентификация пользователей.
    """
    users_data = [
        {"email": "ivan@example.com", "password": "qwerty123!", "password2": "qwerty123!", "first_name": "Ivan",
         "last_name": "Ivanov", "phone": "+7(981)789-09-89", "city": "Moscow"},
        {"email": "petr@example.com", "password": "qwerty123!", "password2": "qwerty123!", "first_name": "Petr",
         "last_name": "Petrov", "phone": "+7(981)789-09-89", "city": "Saint Petersburg"}
    ]
    moderator_data = {
        "email": "staff@example.com", "password": "qwerty123!", "password2": "qwerty123!",
        "first_name": "Staff", "last_name": "User", "phone": "+7(981)789-09-89", "city": "Novosibirsk",
        "is_staff": True
    }

    course_data = [
        {"name": "Python Course", "description": "The best course"},
        {"name": "Java Course", "description": "The best course"}
    ]

    @staticmethod
    def create_authenticated_client(user_data):
        client = APIClient()
        client.post('/api/register/', user_data, format='json')
        if user_data.get('is_staff'):
            user = CustomUser.objects.get(email=user_data["email"])
            user.is_staff = True
            user.save()
        login = client.post('/api/login/', {'email': user_data['email'], 'password': user_data['password']})
        access_token = login.json().get('access')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        return client

    def setUp(self):
        self.user_clients = []
        for user_data in self.users_data:
            client = self.create_authenticated_client(user_data)
            self.user_clients.append(client)

        self.moderator_client = self.create_authenticated_client(self.moderator_data)


class BaseCourseTestCase(BaseTestCase):
    pass


class CourseCreateListTestCase(BaseCourseTestCase):

    def test_user_can_create_course(self):
        """
        Обычный пользователь может создавать курс.
        Обычный пользователь видит только свой курс.
        Модератор не может создавать курс.
        Модератор видит все курсы.
        """

        for i, client in enumerate(self.user_clients):
            new_course = client.post('/api/courses/', self.course_data[i])

            self.assertEqual(new_course.status_code, status.HTTP_201_CREATED)

            courses_for_user_response = client.get('/api/courses/')
            self.assertEqual(courses_for_user_response.status_code, status.HTTP_200_OK)
            courses_for_user = courses_for_user_response.json().get('results')
            self.assertEqual(len(courses_for_user), 1)

        new_course_by_moderator = self.moderator_client.post('/api/courses/', self.course_data[0])
        self.assertEqual(new_course_by_moderator.status_code, status.HTTP_403_FORBIDDEN)

        courses_for_moderator_response = self.moderator_client.get('/api/courses/')
        self.assertEqual(courses_for_moderator_response.status_code, status.HTTP_200_OK)
        courses_for_moderator = courses_for_moderator_response.json().get('results')
        self.assertEqual(len(courses_for_moderator), 2)

    def test_unique_name_course(self):
        """
        Нельзя создать курс с названием, которое уже существует в системе
        """
        course_1 = self.user_clients[0].post('/api/courses/', self.course_data[0])
        course_2 = self.user_clients[0].post('/api/courses/', self.course_data[0])
        self.assertEqual(course_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(course_2.status_code, status.HTTP_400_BAD_REQUEST)


class CourseReadUpdateDeleteTestCase(BaseCourseTestCase):
    def setUp(self):
        """
        Создание курсов.
        Курсы создаются от лица разных пользователей
        дял тестирования доступа.
        """
        super().setUp()
        self.created_courses = []
        self.created_course_ids = []

        self.course_new_data = [
            {"name": "Python Course New", "description": "The best New course"},
            {"name": "Java Course New", "description": "The best New course"}
        ]
        self.course_new_data_partial = [
            {"name": "Python Course The Best"},
            {"name": "Java Course The Best"}
        ]

        for i, client in enumerate(self.user_clients):
            response = client.post('/api/courses/', self.course_data[i])
            self.created_courses.append(response.json())

        for i, course in enumerate(self.created_courses):
            course_id = self.created_courses[i]['id']
            self.created_course_ids.append(course_id)

    def test_creator_can_get_course_detail(self):
        """
        Создатель курса может его прочитать.
        Атрибуты курсов соответствуют ожидаемым.
        """
        for i, course_data in enumerate(self.course_data):
            course_id = self.created_courses[i]['id']
            response = self.user_clients[i].get(f'/api/courses/{course_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            course = response.json()
            self.assertTrue('id' in course)
            self.assertEqual(course['name'], course_data['name'])
            self.assertEqual(course['description'], course_data['description'])
            self.assertEqual(course['preview']['image'], '/media/courses/default.png')
            self.assertEqual(len(course['lessons']), 0)
            self.assertEqual(course['lessons_count'], 0)
            self.assertEqual(course['created_by']['email'], self.users_data[i]['email'])
            self.assertFalse(course['subscribed'])

    def test_non_creator_can_not_get_course_detail(self):
        """
        Если пользователь не является создателем курса и не является модератором,
        он не может его прочитать.
        """
        get_response_user_1 = self.user_clients[0].get(f'/api/courses/{self.created_course_ids[1]}/',
                                                       self.course_new_data[1])
        self.assertEqual(get_response_user_1.status_code, status.HTTP_404_NOT_FOUND)

        get_response_user_2 = self.user_clients[1].get(f'/api/courses/{self.created_course_ids[0]}/',
                                                       self.course_new_data[0])
        self.assertEqual(get_response_user_2.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_creator_can_not_update_course(self):
        """
        Если пользователь не является создателем курса и не является модератором,
        он не может его изменить.
        """
        update_response_user_1 = self.user_clients[0].put(f'/api/courses/{self.created_course_ids[1]}/',
                                                          self.course_new_data[1])
        self.assertEqual(update_response_user_1.status_code, status.HTTP_404_NOT_FOUND)

        update_response_user_2 = self.user_clients[1].put(f'/api/courses/{self.created_course_ids[0]}/',
                                                          self.course_new_data[0])
        self.assertEqual(update_response_user_2.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_creator_can_not_partial_update_course(self):
        """
        Если пользователь не является создателем курса и не является модератором,
        он не может его частично изменить.
        """
        update_response_user_1 = self.user_clients[0].patch(f'/api/courses/{self.created_course_ids[1]}/',
                                                            self.course_new_data[1])
        self.assertEqual(update_response_user_1.status_code, status.HTTP_404_NOT_FOUND)

        update_response_user_2 = self.user_clients[1].patch(f'/api/courses/{self.created_course_ids[0]}/',
                                                            self.course_new_data[0])
        self.assertEqual(update_response_user_2.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderator_can_get_courses_detail(self):
        """
        Модератор может видеть все курсы.
        Атрибуты соответствуют ожидаемым.
        """
        for i, course_data in enumerate(self.course_data):
            course_id = self.created_courses[i]['id']
            response = self.moderator_client.get(f'/api/courses/{course_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            course = response.json()
            self.assertTrue('id' in course)
            self.assertEqual(course['name'], course_data['name'])
            self.assertEqual(course['description'], course_data['description'])
            self.assertEqual(course['preview']['image'], '/media/courses/default.png')
            self.assertEqual(len(course['lessons']), 0)
            self.assertEqual(course['lessons_count'], 0)
            self.assertEqual(course['created_by']['email'], self.users_data[i]['email'])
            self.assertFalse(course['subscribed'])

    def test_moderator_can_update_courses(self):
        """
        Модератор может менять все курсы.
        Атрибуты соответствуют ожидаемым после изменения.
        """
        for i, course_data in enumerate(self.course_data):
            course_id = self.created_courses[i]['id']
            response = self.moderator_client.put(f'/api/courses/{course_id}/', self.course_new_data[i])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            course = response.json()
            self.assertTrue('id' in course)
            self.assertEqual(course['name'], self.course_new_data[i]['name'])
            self.assertEqual(course['description'], self.course_new_data[i]['description'])
            self.assertEqual(course['preview']['image'], '/media/courses/default.png')
            self.assertEqual(len(course['lessons']), 0)
            self.assertEqual(course['lessons_count'], 0)
            self.assertEqual(course['created_by']['email'], self.users_data[i]['email'])
            self.assertFalse(course['subscribed'])

    def test_moderator_can_partial_update_courses(self):
        """
        Модератор может частично менять все курсы.
        Атрибуты соответствуют ожидаемым после частичного изменения.
        """
        for i, course_data in enumerate(self.course_data):
            course_id = self.created_courses[i]['id']
            response = self.moderator_client.patch(f'/api/courses/{course_id}/', self.course_new_data_partial[i])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            course = response.json()
            self.assertTrue('id' in course)
            self.assertEqual(course['name'], self.course_new_data_partial[i]['name'])
            self.assertEqual(course['description'], self.course_data[i]['description'])
            self.assertEqual(course['preview']['image'], '/media/courses/default.png')
            self.assertEqual(len(course['lessons']), 0)
            self.assertEqual(course['lessons_count'], 0)
            self.assertEqual(course['created_by']['email'], self.users_data[i]['email'])
            self.assertFalse(course['subscribed'])

    def test_moderator_can_not_delete_courses(self):
        """
        Модератор не может удалить курс.
        """
        for course_id in self.created_course_ids:
            response = self.moderator_client.delete(f'/api/courses/{course_id}/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_creator_can_not_delete_course(self):
        """
        Если пользователь не создатель, он не может удалить курс.
        """
        delete_response_user_1 = self.user_clients[0].delete(f'/api/courses/{self.created_course_ids[1]}/')
        self.assertEqual(delete_response_user_1.status_code, status.HTTP_404_NOT_FOUND)

        delete_response_user_2 = self.user_clients[1].delete(f'/api/courses/{self.created_course_ids[0]}/')
        self.assertEqual(delete_response_user_2.status_code, status.HTTP_404_NOT_FOUND)

    def test_creator_can_delete_course(self):
        """
        Если пользователь создатель, он может удалить курс.
        """
        for i, course_data in enumerate(self.course_data):
            course_id = self.created_courses[i]['id']
            response = self.user_clients[i].delete(f'/api/courses/{course_id}/')
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            courses = self.user_clients[i].get(f'/api/courses/{course_id}/')
            self.assertEqual(courses.status_code, status.HTTP_404_NOT_FOUND)
