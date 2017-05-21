INSERT_OPERATION_ADD = '''INSERT INTO operation (client_id, host_id, income, outcome, bill) 
                      SELECT client.client_id, %s, %s, 0, %s
                      FROM client WHERE identificator = %s;'''

INSERT_OPERATION_WITHDRAW = '''INSERT INTO operation (client_id, host_id, income, outcome, bill) 
                      SELECT client.client_id, %s, 0,%s, %s
                      FROM client WHERE identificator = %s;'''

SELECT_STATISTIC = '''SELECT DATE(operation_date), AVG(bill), SUM(income), SUM(outcome) FROM operation
                      WHERE host_id = %s
                      GROUP BY DATE (operation_date);'''

SELECT_INFO= '''SELECT title, description, address, time_open, time_close, profile_image FROM host
                WhERE host_id = %s;'''

EDIT_HOST = '''UPDATE host SET title = %s, description = %s, address = %s, time_open = %s, time_close = %s
               WHERE host_id = %s;'''

UPLOAD_PHOTO = '''UPDATE host SET profile_image = %s WHERE host_id = %s;'''

GET_USER_FROM_CREDENTAIL = '''SELECT user_id FROM user WHERE login = %s and password = %s;'''

CHECK_USER_FROM_LOGIN = '''SELECT user_id FROM user WHERE login = %s;'''

INSERT_USER = '''INSERT INTO user (login, password) VALUES (%s, %s)'''

INSERT_HOST = '''INSERT INTO host (user_id) VALUES (%s);'''
UPDATE_NEW_HOST = '''UPDATE host SET title=%s, description=%s, address=%s, time_open=%s, time_close=%s WHERE host_id = %s;'''

CHECK_HOST_CLIENT = '''SELECT * FROM client_host WHERE host_id = %s and client_id = (SELECT client_id FROM client WHERE identificator = %s); '''

INSERT_CLIENT_HOST = '''INSERT INTO client_host (client_id, host_id, points)
                        SELECT client.client_id, %s, 0
                        FROM client WHERE identificator = %s;'''

SELECT_ALL_HOSTS = '''SELECT host_id FROM host;'''