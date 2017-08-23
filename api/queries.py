INSERT_OPERATION_ADD = '''INSERT INTO transactions (client_id, host_id, amount, type_id) 
                      SELECT client.client_id, %s, %s, 0, %s
                      FROM client WHERE identificator = %s;'''

INSERT_OPERATION_WITHDRAW = '''INSERT INTO transactions (client_id, host_id, amount, type_id) 
                      SELECT client.client_id, %s, 0,%s, %s
                      FROM client WHERE identificator = %s;'''

# SELECT_STATISTIC = '''SELECT DATE(transactions_date), AVG(bill), SUM(income), SUM(outcome) FROM transactions
#                       WHERE host_id = %s
#                       GROUP BY DATE (transactions_date);'''

SELECT_INFO= '''SELECT title, description, address, time_open, time_close, profile_image FROM host
                WhERE host_id = %s;'''

EDIT_HOST = '''UPDATE host SET title = %s, description = %s, address = %s, time_open = %s, time_close = %s
               WHERE host_id = %s;'''

UPLOAD_PHOTO = '''UPDATE host SET profile_image = %s WHERE host_id = %s;'''

GET_USER_FROM_CREDENTAIL = '''SELECT user_id FROM user WHERE login = %s and password = %s;'''

CHECK_USER_FROM_LOGIN = '''SELECT user_id FROM user WHERE login = %s;'''

INSERT_USER = '''INSERT INTO user (login, password) VALUES (%s, %s)'''

INSERT_HOST = '''INSERT INTO host (user_id) VALUES (%s);'''

INSERT_CLIENT = '''INSERT INTO client (name, identificator, user_id) VALUES (%s, %s, %s);'''
UPDATE_NEW_HOST = '''UPDATE host SET title=%s, description=%s, address=%s, time_open=%s, time_close=%s, add_percent = %s WHERE host_id = %s;'''

CHECK_HOST_CLIENT = '''SELECT * FROM score WHERE host_id = %s and client_id = (SELECT client_id FROM client WHERE identificator = %s); '''

INSERT_CLIENT_HOST = '''INSERT INTO score (client_id, host_id, amount)
                        SELECT client.client_id, %s, 0
                        FROM client WHERE identificator = %s;'''

SELECT_ALL_HOSTS = '''SELECT host_id FROM host;'''

SELECT_NAME_IDENTIFICATOR_FROM_CLIENT = '''SELECT name, identificator FROM client WHERE client_id = %s;'''