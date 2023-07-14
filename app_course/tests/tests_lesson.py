from rest_framework import status

from app_course.tests.tests_course import BaseTestCase


class BaseLessonTestCase(BaseTestCase):
    """
    Расширяет настройки базового тест-кейса.
    Создание курсов от лица разных пользователей
    (урок ссылается на курс, поэтому необходимо создать курс).
    """
    lessons_data = [
        {
            "name": "Делаю игру Змейка на Python.",
            "description": "Делаю игру Змейка на Python.",
            "video_url": "https://www.youtube.com/watch?v=FTtEF1KDBXo",
            "course": None
        },
        {
            "name": "Что такое Java и как ее выучить?",
            "description": "Что такое Java и как ее выучить?",
            "video_url": "https://www.youtube.com/watch?v=uLESJ4atN-U",
            "course": None
        }
    ]
    lesson_data_with_bad_video_url = {
        "name": "Что такое Java",
        "description": "Что такое Java",
        "video_url": "https://aws.amazon.com/ru/what-is/java/",
        "course": None
    }

    def setUp(self):
        super().setUp()
        self.created_courses = []
        self.created_course_ids = []

        for i, client in enumerate(self.user_clients):
            response = client.post('/api/courses/', self.course_data[i])
            self.created_courses.append(response.json())

        for i, course in enumerate(self.created_courses):
            course_id = self.created_courses[i]['id']
            self.created_course_ids.append(course_id)

        for i, lesson_data in enumerate(self.lessons_data):
            lesson_data["course"] = self.created_course_ids[i]

        self.lesson_data_with_bad_video_url["course"] = self.created_course_ids[1]


class LessonCreateListTestCase(BaseLessonTestCase):
    def test_user_can_create_lesson(self):
        """
        Обычный пользователь может создавать урок.
        Обычный пользователь видит только свой урок.
        Модератор не может создавать урок.
        Модератор видит все уроки.
        """

        for i, client in enumerate(self.user_clients):
            new_lesson = client.post('/api/lessons/', self.lessons_data[i])

            self.assertEqual(new_lesson.status_code, status.HTTP_201_CREATED)

            lessons_for_user_response = client.get('/api/lessons/')
            self.assertEqual(lessons_for_user_response.status_code, status.HTTP_200_OK)
            lessons_for_user = lessons_for_user_response.json().get('results')
            self.assertEqual(len(lessons_for_user), 1)

        new_lesson_by_moderator = self.moderator_client.post('/api/lessons/', self.lessons_data[0])
        self.assertEqual(new_lesson_by_moderator.status_code, status.HTTP_403_FORBIDDEN)

        lessons_for_moderator_response = self.moderator_client.get('/api/lessons/')
        self.assertEqual(lessons_for_moderator_response.status_code, status.HTTP_200_OK)
        lessons_for_moderator = lessons_for_moderator_response.json().get('results')
        self.assertEqual(len(lessons_for_moderator), 2)

    def test_unique_name_course(self):
        """
        Нельзя создать урок с названием, которое уже существует в системе
        """
        lesson_1 = self.user_clients[0].post('/api/lessons/', self.lessons_data[0])
        lesson_2 = self.user_clients[0].post('/api/lessons/', self.lessons_data[0])
        self.assertEqual(lesson_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(lesson_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_not_create_lesson_with_video_url_not_youtube(self):
        """
        При создании урока можно использовать только ссылки на YouTube
        """
        lesson = self.user_clients[0].post('/api/lessons/', self.lesson_data_with_bad_video_url)
        self.assertEqual(lesson.status_code, status.HTTP_400_BAD_REQUEST)


class LessonReadUpdateDeleteTestCase(BaseLessonTestCase):
    def setUp(self):
        """
        Создание уроков.
        Уроки создаются от лица разных пользователей
        для тестирования доступа.
        """
        super().setUp()

        self.lessons_new_data = [
            {
                "name": "Делаю игру Змейка на Python NEW",
                "description": "Делаю игру Змейка на Python NEW",
                "video_url": "https://www.youtube.com/watch?v=FTtEF1KDBXo",
                "course": None
            },
            {
                "name": "Что такое Java и как ее выучить NEW",
                "description": "Что такое Java и как ее выучить NEW",
                "video_url": "https://www.youtube.com/watch?v=uLESJ4atN-U",
                "course": None
            }
        ]
        self.lessons_new_data_partial = [
            {"name": "Python Lesson The Best"},
            {"name": "Java Lesson The Best"}
        ]

        self.created_lessons = []
        self.created_lesson_ids = []

        for i, lesson_new_data in enumerate(self.lessons_new_data):
            lesson_new_data["course"] = self.created_course_ids[i]

        for i, client in enumerate(self.user_clients):
            response = client.post('/api/lessons/', self.lessons_data[i])
            self.created_lessons.append(response.json())

        for i, lessons in enumerate(self.created_lessons):
            lesson_id = self.created_lessons[i]['id']
            self.created_lesson_ids.append(lesson_id)

    def test_creator_can_get_lesson_detail(self):
        """
        Создатель урока может его прочитать.
        Атрибуты уроков соответствуют ожидаемым.
        В курсе появляется информация о связанных уроках и их количестве.
        """
        for i, lesson_data in enumerate(self.lessons_data):
            lesson_id = self.created_lessons[i]['id']
            response = self.user_clients[i].get(f'/api/lessons/{lesson_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            lesson = response.json()
            self.assertTrue('id' in lesson)
            self.assertEqual(lesson['name'], lesson_data['name'])
            self.assertEqual(lesson['description'], lesson_data['description'])
            self.assertEqual(lesson['preview']['image'], '/media/lessons/default.png')
            self.assertEqual(lesson['video_url'], lesson_data['video_url'])
            self.assertEqual(lesson['course'], lesson_data['course'])
            self.assertEqual(lesson['created_by']['email'], self.users_data[i]['email'])

            course_response = self.user_clients[i].get(f'/api/courses/{lesson_data["course"]}/')
            lesson_info = course_response.json()['lessons']
            lessons_count = course_response.json()['lessons_count']
            self.assertEqual(lesson_info[0]['name'], lesson_data['name'])
            self.assertEqual(lessons_count, 1)

    def test_non_creator_can_not_get_lesson_detail(self):
        """
        Если пользователь не является создателем урока и не является модератором,
        он не может его прочитать.
        """
        get_response_user_1 = self.user_clients[0].get(f'/api/lessons/{self.created_lesson_ids[1]}/',
                                                       self.lessons_new_data[1])
        self.assertEqual(get_response_user_1.status_code, status.HTTP_403_FORBIDDEN)

        get_response_user_2 = self.user_clients[1].get(f'/api/lessons/{self.created_lesson_ids[0]}/',
                                                       self.lessons_new_data[0])
        self.assertEqual(get_response_user_2.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_creator_can_not_update_lesson_detail(self):
        """
        Если пользователь не является создателем урока и не является модератором,
        он не может его изменить.
        """
        get_response_user_1 = self.user_clients[0].put(f'/api/lessons/{self.created_lesson_ids[1]}/',
                                                       self.lessons_new_data[1])
        self.assertEqual(get_response_user_1.status_code, status.HTTP_403_FORBIDDEN)

        get_response_user_2 = self.user_clients[1].put(f'/api/lessons/{self.created_lesson_ids[0]}/',
                                                       self.lessons_new_data[0])
        self.assertEqual(get_response_user_2.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_creator_can_not_partial_update_lesson_detail(self):
        """
        Если пользователь не является создателем урока и не является модератором,
        он не может его изменить.
        """
        get_response_user_1 = self.user_clients[0].patch(f'/api/lessons/{self.created_lesson_ids[1]}/',
                                                         self.lessons_new_data[1])
        self.assertEqual(get_response_user_1.status_code, status.HTTP_403_FORBIDDEN)

        get_response_user_2 = self.user_clients[1].patch(f'/api/lessons/{self.created_lesson_ids[0]}/',
                                                         self.lessons_new_data[0])
        self.assertEqual(get_response_user_2.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_get_lesson_detail(self):
        """
        Модератор может видеть все уроки.
        Атрибуты соответствуют ожидаемым.
        """
        for i, lesson_data in enumerate(self.lessons_data):
            lesson_id = self.created_lessons[i]['id']
            response = self.moderator_client.get(f'/api/lessons/{lesson_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            lesson = response.json()
            self.assertTrue('id' in lesson)
            self.assertEqual(lesson['name'], lesson_data['name'])
            self.assertEqual(lesson['description'], lesson_data['description'])
            self.assertEqual(lesson['preview']['image'], '/media/lessons/default.png')
            self.assertEqual(lesson['video_url'], lesson_data['video_url'])
            self.assertEqual(lesson['course'], lesson_data['course'])
            self.assertEqual(lesson['created_by']['email'], self.users_data[i]['email'])

    def test_moderator_can_update_lesson_detail(self):
        """
        Модератор может редактировать все уроки.
        Атрибуты соответствуют ожидаемым.
        """
        for i, lesson_data in enumerate(self.lessons_data):
            lesson_id = self.created_lessons[i]['id']
            response = self.moderator_client.put(f'/api/lessons/{lesson_id}/', self.lessons_new_data[i])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            lesson = response.json()
            self.assertTrue('id' in lesson)
            self.assertEqual(lesson['name'], self.lessons_new_data[i]['name'])
            self.assertEqual(lesson['description'], self.lessons_new_data[i]['description'])
            self.assertEqual(lesson['preview']['image'], '/media/lessons/default.png')
            self.assertEqual(lesson['video_url'], self.lessons_new_data[i]['video_url'])
            self.assertEqual(lesson['course'], self.lessons_new_data[i]['course'])
            self.assertEqual(lesson['created_by']['email'], self.users_data[i]['email'])

    def test_moderator_can_partial_update_lesson_detail(self):
        """
        Модератор может частично редактировать все уроки.
        Атрибуты соответствуют ожидаемым.
        """
        for i, lesson_data in enumerate(self.lessons_data):
            lesson_id = self.created_lessons[i]['id']
            response = self.moderator_client.patch(f'/api/lessons/{lesson_id}/', self.lessons_new_data_partial[i])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            lesson = response.json()
            self.assertTrue('id' in lesson)
            self.assertEqual(lesson['name'], self.lessons_new_data_partial[i]['name'])
            self.assertEqual(lesson['description'], self.lessons_data[i]['description'])
            self.assertEqual(lesson['preview']['image'], '/media/lessons/default.png')
            self.assertEqual(lesson['video_url'], self.lessons_data[i]['video_url'])
            self.assertEqual(lesson['course'], self.lessons_data[i]['course'])
            self.assertEqual(lesson['created_by']['email'], self.users_data[i]['email'])

    def test_moderator_can_not_delete_lessons(self):
        """
        Модератор не может удалить урок.
        """
        for lesson_id in self.created_lesson_ids:
            response = self.moderator_client.delete(f'/api/courses/{lesson_id}/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_creator_can_not_delete_course(self):
        """
        Если пользователь не создатель, он не может удалить урок.
        """
        delete_response_user_1 = self.user_clients[0].delete(f'/api/lessons/{self.created_lesson_ids[1]}/')
        self.assertEqual(delete_response_user_1.status_code, status.HTTP_403_FORBIDDEN)

        delete_response_user_2 = self.user_clients[1].delete(f'/api/lessons/{self.created_lesson_ids[0]}/')
        self.assertEqual(delete_response_user_2.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_can_delete_course(self):
        """
        Если пользователь создатель, он может удалить урок.
        """
        for i, lesson_data in enumerate(self.lessons_data):
            lesson_id = self.created_lessons[i]['id']
            response = self.user_clients[i].delete(f'/api/lessons/{lesson_id}/')
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            courses = self.user_clients[i].get(f'/api/lessons/{lesson_id}/')
            self.assertEqual(courses.status_code, status.HTTP_404_NOT_FOUND)
