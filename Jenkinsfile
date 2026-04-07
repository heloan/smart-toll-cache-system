// Jenkinsfile — CI/CD pipeline definition for Smart Toll Cache System

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Rodovia') {
            steps {
                sh 'cd services/rodovia && ./mvnw clean package -DskipTests'
            }
        }
        stage('Build Frontend') {
            steps {
                sh 'cd services/toll-frontend-react && npm ci && npm run build'
            }
        }
        stage('Install Simulador Deps') {
            steps {
                sh 'cd services/simulador && pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh './tests/scripts/run-all-tests.sh'
            }
        }
        stage('Docker Build') {
            steps {
                sh 'docker-compose -f infrastructure/docker-compose.yml build'
            }
        }
        stage('Deploy') {
            steps {
                sh './scripts/start.sh'
            }
        }
    }
}
