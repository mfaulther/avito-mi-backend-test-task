# avito-mi-backend-test-task
Тестовое задание на позицию Backend-стажёр в юнит Market Intelligence (Python)
### Важно 
Данные в приложении собираются через API Авито, поэтому перед запуском в Dockerfile нужно указать API_KEY
## Методы
### 1. POST /add
Принмает на вход данные пары регион + запрос в формате JSON, возвращает id созданной пары

POST /add  {"query":  , "region": }

Результат: 
{"id": 1}

### 2. GET /stat/id?=
Принимает в качестве параметра id пары регион + запрос. Возвращает временные метки

GET /stat/id?=5

Результат:


[

      {"count":2606,"time":"16:57 14/12/20"},
  
      {"count":2606,"time":"17:57 14/12/20"},
  
      {"count":2606,"time":"18:57 14/12/20"},
  
      {"count":2606,"time":"19:57 14/12/20"}
  
]
