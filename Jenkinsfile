pipeline {
    agent any

    environment {
        IMAGE_NAME = 'anatabudiayuni/simple-app'
        REGISTRY_CREDENTIALS = 'dockerhub-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                bat 'echo Mulai build aplikasi'
                bat 'docker version'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME%:%BUILD_NUMBER% ."
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS,
                        usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    withEnv(["DOCKER_CONFIG=${env.WORKSPACE}\\.docker-push"]) {
                        bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                        bat "docker push %IMAGE_NAME%:%BUILD_NUMBER%"
                        bat "docker tag %IMAGE_NAME%:%BUILD_NUMBER% %IMAGE_NAME%:latest"
                        bat "docker push %IMAGE_NAME%:latest"
                        bat 'docker logout'
                    }
                }
            }
        }

        stage('Deploy (App + Database)') {
            steps {
                bat 'docker compose up -d --build'
                bat 'docker compose ps'
            }
        }
    }

    post {
        always {
            echo 'Selesai build'
        }
    }
}
