pipeline {
    agent {
        kubernetes {
            yaml '''
            spec:
              containers:
              - name: python
                image: python:3.12-slim
                command: ['sleep', 'infinity']
            '''
        }
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/DerbSwag/Devops-fastapi-lab.git'
            }
        }
        stage('Install & Test') {
            steps {
                container('python') {
                    sh '''
                        pip install -r app/requirements.txt --quiet
                        python -c "from app.main import app; print('✅ FastAPI app imports OK')"
                    '''
                }
            }
        }
        stage('Info') {
            steps {
                container('python') {
                    sh 'python --version && pip list | grep -i "fastapi\\|sqlalchemy\\|uvicorn"'
                }
            }
        }
    }
    post {
        success { echo '✅ Pipeline SUCCESS' }
        failure { echo '❌ Pipeline FAILED' }
    }
}
