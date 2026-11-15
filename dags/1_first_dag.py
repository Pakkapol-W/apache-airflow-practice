from airflow.decorators import dag, task 

@dag(
        dag_id="first_dag"
)
def first_dag():

    @task
    def first_task():
        print("this is the first task")
        
    @task
    def second_task():
        print("this is the second task")

        
    @task
    def third_task():
        print("this is the third task")

    first = first_task()
    second = second_task()
    third = third_task()

    first >> second >> third

first_dag()