from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

with DAG(
    dag_id="03-python-operator",
    schedule="*/10 * * * *",
    start_date=pendulum.datetime(2024, 10, 30, tz="Asia/Seoul"),
    catchup=False
) as dag:
    def name_time(format: str):
        now = datetime.now()
        kr_time = now + timedelta(hours=9)
        msg = kr_time.strftime("지금은 %Y년 %m월 %d일 %H시 %M분 %S초입니다\n") + "제 이름은 류경표입니다."
        return msg
    
    def send_email(**kwagrs):
        name_time_contents = kwagrs['ti'].xcom_pull(task_ids='name_time_task')
        # ti: task_instance
        
        email_operator = EmailOperator(
            task_id='send_email_task', # task_id와 변수명 일치시키기
            to='kyongpyo0626@gmail.com',
            subject='[Airflow] ✅ Success !',
            html_content=f' DAG: {{ {{task_instance.dag_id}} }}<br> Task: {{ {{task_instance.task_id}} }}<br> Execution Time: {{ {{ts}} }}<br> Log URL: {{ {{task_instance.log_url}} }}<br> Message: { name_time_contents }'
            # cc="" # 참조
        )
        email_operator.execute(context=kwagrs)

    name_time_task = PythonOperator(
        task_id='name_time_task',
        python_callable=name_time,
        op_kwargs={'format':'txt'},
    )
    
    send_email_task = PythonOperator(
        task_id='send_email_task',
        python_callable=send_email, # 여기세 함수명을 주는거 (이거로 함수실행함)
        provide_context=True,  # XCom을 사용하기 위해 필요
    )

    name_time_task >> send_email_task