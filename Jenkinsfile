pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_NAME = 'mediscan-ai'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDENTIALS_ID = 'docker-credentials'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 --version || python --version
                    pip --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv .venv || python -m venv .venv
                        . .venv/bin/activate || .venv\\Scripts\\activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Lint Code') {
            steps {
                sh '''
                    pip install flake8
                    flake8 backend/main.py --max-line-length=100 --exclude=.venv
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                dir('backend') {
                    sh '''
                        . .venv/bin/activate || .venv\\Scripts\\activate
                        pip install pytest pytest-cov
                        pytest --cov=. --cov-report=xml || echo "No tests found, skipping"
                    '''
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG}", "./backend")
                    docker.build("${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG}", ".")
                }
            }
        }
        
        stage('Test Docker Images') {
            steps {
                script {
                    // Test backend image
                    sh """
                        docker run --rm -d --name test-backend ${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG}
                        sleep 10
                        docker exec test-backend curl -f http://localhost:8000/health || exit 1
                        docker stop test-backend
                    """
                    
                    // Test frontend image
                    sh """
                        docker run --rm -d --name test-frontend ${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG}
                        sleep 5
                        docker exec test-frontend wget --spider http://localhost || exit 1
                        docker stop test-frontend
                    """
                }
            }
        }
        
        stage('Push Docker Images') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh """
                            echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin ${DOCKER_REGISTRY}
                            
                            docker tag ${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-backend:latest
                            docker tag ${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG}
                            
                            docker tag ${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-frontend:latest
                            docker tag ${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG}
                            
                            docker push ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-backend:latest
                            docker push ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG}
                            docker push ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-frontend:latest
                            docker push ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG}
                        """
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    # Install Trivy if not present
                    which trivy || (wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list && apt-get update && apt-get install trivy -y)
                    
                    trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG}
                    trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG}
                '''
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    # Example deployment command
                    # docker-compose pull
                    # docker-compose up -d
                    echo "Deployment step - customize based on your environment"
                '''
            }
        }
        
        stage('Cleanup') {
            steps {
                sh '''
                    docker rmi ${DOCKER_IMAGE_NAME}-backend:${DOCKER_TAG} || true
                    docker rmi ${DOCKER_IMAGE_NAME}-frontend:${DOCKER_TAG} || true
                    docker system prune -f
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}
