// pipeline {
//     agent {
//         docker {
//             image 'jibolaolu/jenkins-agent:latest'
//             args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
//         }
//     }
//
//     environment {
//         AWS_REGION = 'eu-west-2'  // Change to your AWS region
//     }
//
//     stages {
//         stage('Retrieve AWS Account ID') {
//             steps {
//                 withCredentials([[
//                     $class: 'AmazonWebServicesCredentialsBinding',
//                     credentialsId: 'aws_credentials',
//                     accessKeyVariable: 'AWS_ACCESS_KEY_ID',
//                     secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
//                 ]]) {
//                     script {
//                         env.AWS_ACCOUNT_ID = sh(script: """
//                             aws sts get-caller-identity --query 'Account' --output text
//                         """, returnStdout: true).trim()
//                         env.ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
//                         echo "✅ Using AWS Account ID: ${env.AWS_ACCOUNT_ID}"
//                     }
//                 }
//             }
//         }
//
//         stage('Checkout Code') {
//             steps {
//                 script {
//                     echo 'Checking out source code...'
//                     checkout([$class: 'GitSCM',
//                         branches: [[name: '*/master']],
//                         extensions: [[$class: 'WipeWorkspace']],
//                         userRemoteConfigs: [[
//                             credentialsId: 'github-credentials',
//                             url: 'https://github.com/jibolaolu/stock-repo.git'
//                         ]]
//                     ])
//                 }
//             }
//         }
//
//         stage('Verify Git Directory') {
//             steps {
//                 script {
//                     sh "git status"  // Ensure we are inside a valid git repo
//                 }
//             }
//         }
//
//         stage('Get Latest Version from ECR') {
//             steps {
//                 script {
//                     def repoNames = ['teach-bleats-frontend', 'teach-bleats-backend', 'teach-bleats-cache']
//                     env.VERSION_NUMBER = "1.0.0"  // Default if no version exists
//
//                     for (repo in repoNames) {
//                         def lastTag = sh(script: """
//                             aws ecr describe-images --repository-name ${repo} --region ${AWS_REGION} --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' --output text 2>/dev/null || echo "none"
//                         """, returnStdout: true).trim()
//
//                         if (lastTag == "none") {
//                             echo "No previous version found for ${repo}, starting from ${env.VERSION_NUMBER}"
//                         } else {
//                             echo "Last version in ${repo}: ${lastTag}"
//                             def versionParts = lastTag.tokenize('.')
//                             if (versionParts.size() == 3) {
//                                 versionParts[2] = (versionParts[2].toInteger() + 1).toString()
//                                 env.VERSION_NUMBER = versionParts.join('.')
//                             }
//                         }
//                     }
//
//                     echo "Using new version: ${env.VERSION_NUMBER}"
//                 }
//             }
//         }
//
//         stage('Detect Changes') {
//             steps {
//                 script {
//                     def changedFiles = sh(script: "git diff --name-only HEAD^ HEAD", returnStdout: true).trim().split("\n")
//                     echo "Changed Files: ${changedFiles}"
//
//                     env.BUILD_FRONTEND = "false"
//                     env.BUILD_BACKEND = "false"
//                     env.BUILD_CACHE = "false"
//
//                     for (file in changedFiles) {
//                         if (file.startsWith("frontend/")) {
//                             env.BUILD_FRONTEND = "true"
//                         }
//                         if (file.startsWith("backend/")) {
//                             env.BUILD_BACKEND = "true"
//                         }
//                         if (file.startsWith("cache/")) {
//                             env.BUILD_CACHE = "true"
//                         }
//                         if (file == "Dockerfile" || file == ".env") {
//                             env.BUILD_FRONTEND = "true"
//                             env.BUILD_BACKEND = "true"
//                             env.BUILD_CACHE = "true"
//                         }
//                     }
//
//                     echo "Frontend Changed: ${env.BUILD_FRONTEND}"
//                     echo "Backend Changed: ${env.BUILD_BACKEND}"
//                     echo "Cache Changed: ${env.BUILD_CACHE}"
//                 }
//             }
//         }
//
//         stage('Login to AWS ECR') {
//     steps {
//         withCredentials([[
//             $class: 'AmazonWebServicesCredentialsBinding',
//             credentialsId: 'aws_credentials',
//             accessKeyVariable: 'AWS_ACCESS_KEY_ID',
//             secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
//         ]]) {
//             script {
//                 echo '🔐 Logging into AWS ECR...'
//                 sh """
//                     export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
//                     export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY
//                     export HOME=\$WORKSPACE
//                     aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}
//                 """
//             }
//         }
//     }
// }
//
//         stage('Build & Push Docker Images') {
//             parallel {
//                 stage('Build & Push Frontend') {
//                     when {
//                         expression { env.BUILD_FRONTEND == "true" }
//                     }
//                     steps {
//                         script {
//                             def imageTag = "${env.VERSION_NUMBER}"
//                             def ecrRepo = "${env.ECR_REGISTRY}/teach-bleats-frontend"
//
//                             echo "Building Frontend Image: ${ecrRepo}:${imageTag}"
//
//                             sh """
//                                 cd frontend
//                                 docker build -t frontend .
//                                 docker tag frontend:${imageTag} ${ecrRepo}:${imageTag}
//                                 docker push ${ecrRepo}:${imageTag}
//                             """
//                         }
//                     }
//                 }
//
//                 stage('Build & Push Backend') {
//                     when {
//                         expression { env.BUILD_BACKEND == "true" }
//                     }
//                     steps {
//                         script {
//                             def imageTag = "${env.VERSION_NUMBER}"
//                             def ecrRepo = "${env.ECR_REGISTRY}/teach-bleats-backend"
//
//                             echo "Building Backend Image: ${ecrRepo}:${imageTag}"
//
//                             sh """
//                                 cd backend
//                                 docker build -t backend .
//                                 docker tag backend:${imageTag} ${ecrRepo}:${imageTag}
//                                 docker push ${ecrRepo}:${imageTag}
//                             """
//                         }
//                     }
//                 }
//
//                 stage('Build & Push Cache') {
//                     when {
//                         expression { env.BUILD_CACHE == "true" }
//                     }
//                     steps {
//                         script {
//                             def imageTag = "${env.VERSION_NUMBER}"
//                             def ecrRepo = "${env.ECR_REGISTRY}/teach-bleats-cache"
//
//                             echo "Building Cache Image: ${ecrRepo}:${imageTag}"
//
//                             sh """
//                                 cd cache
//                                 docker build -t cache .
//                                 docker tag cache:${imageTag} ${ecrRepo}:${imageTag}
//                                 docker push ${ecrRepo}:${imageTag}
//                             """
//                         }
//                     }
//                 }
//             }
//         }
//     }
//
//     post {
//         success {
//             echo "✅ Docker images (version ${env.VERSION_NUMBER}) built & pushed to AWS ECR successfully!"
//         }
//         failure {
//             echo "❌ Pipeline failed!"
//         }
//     }
// }

pipeline {
    agent {
        docker {
            image 'jibolaolu/jenkins-agent:latest'
            args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        AWS_REGION = 'eu-west-2'
    }

    stages {
        stage('Retrieve AWS Account ID') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws_credentials',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                ]]) {
                    script {
                        env.AWS_ACCOUNT_ID = sh(script: """
                            aws sts get-caller-identity --query 'Account' --output text
                        """, returnStdout: true).trim()
                        env.ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        echo "✅ Using AWS Account ID: ${env.AWS_ACCOUNT_ID}"
                    }
                }
            }
        }

        stage('Checkout Code') {
            steps {
                script {
                    echo 'Checking out source code...'
                    checkout([$class: 'GitSCM',
                        branches: [[name: '*/master']],
                        extensions: [[$class: 'WipeWorkspace']],
                        userRemoteConfigs: [[
                            credentialsId: 'github-credentials',
                            url: 'https://github.com/jibolaolu/stock-repo.git'
                        ]]
                    ])
                }
            }
        }

        stage('Verify Git Directory') {
            steps {
                script {
                    sh "git status"
                }
            }
        }

        stage('Get Latest Version from ECR') {
            steps {
                script {
                    def repoNames = ['teach-bleats-frontend', 'teach-bleats-backend', 'teach-bleats-cache']

                    env.VERSION_MAP = [:]

                    for (repo in repoNames) {
                        def lastTag = sh(script: """
                            aws ecr describe-images --repository-name ${repo} --region ${AWS_REGION} \
                            --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' --output text 2>/dev/null || echo "none"
                        """, returnStdout: true).trim()

                        def newVersion = "1.0.0"
                        if (lastTag != "none") {
                            def parts = lastTag.tokenize('.')
                            if (parts.size() == 3) {
                                parts[2] = (parts[2].toInteger() + 1).toString()
                                newVersion = parts.join('.')
                            }
                        }

                        env.VERSION_MAP[repo] = newVersion
                        echo "Repo ${repo} new version: ${newVersion}"
                    }
                }
            }
        }

        stage('Detect Changes') {
            steps {
                script {
                    def changedFiles = sh(script: "git diff --name-only HEAD^ HEAD", returnStdout: true).trim().split("\n")
                    echo "Changed Files: ${changedFiles}"

                    env.BUILD_FRONTEND = "false"
                    env.BUILD_BACKEND = "false"
                    env.BUILD_CACHE = "false"

                    for (file in changedFiles) {
                        if (file.startsWith("frontend/")) {
                            env.BUILD_FRONTEND = "true"
                        }
                        if (file.startsWith("backend/")) {
                            env.BUILD_BACKEND = "true"
                        }
                        if (file.startsWith("cache/")) {
                            env.BUILD_CACHE = "true"
                        }
                        if (file == "Dockerfile" || file == ".env") {
                            env.BUILD_FRONTEND = "true"
                            env.BUILD_BACKEND = "true"
                            env.BUILD_CACHE = "true"
                        }
                    }

                    echo "Frontend Changed: ${env.BUILD_FRONTEND}"
                    echo "Backend Changed: ${env.BUILD_BACKEND}"
                    echo "Cache Changed: ${env.BUILD_CACHE}"
                }
            }
        }

        stage('Login to AWS ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws_credentials',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                ]]) {
                    script {
                        echo '🔐 Logging into AWS ECR...'
                        sh """
                            export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY
                            export HOME=\$WORKSPACE
                            mkdir -p \$WORKSPACE/.docker
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin --config \$WORKSPACE/.docker ${env.ECR_REGISTRY}
                        """
                    }
                }
            }
        }

        stage('Build & Push Docker Images') {
            parallel {
                stage('Build & Push Frontend') {
                    when {
                        expression { env.BUILD_FRONTEND == "true" }
                    }
                    steps {
                        script {
                            def imageTag = env.VERSION_MAP['teach-bleats-frontend']
                            def ecrRepo = "${env.ECR_REGISTRY}/teach-bleats-frontend"

                            echo "Building Frontend Image: ${ecrRepo}:${imageTag}"

                            sh """
                                cd frontend
                                docker build -t frontend .
                                docker tag frontend:${imageTag} ${ecrRepo}:${imageTag}
                                docker push ${ecrRepo}:${imageTag}
                            """
                        }
                    }
                }

                stage('Build & Push Backend') {
                    when {
                        expression { env.BUILD_BACKEND == "true" }
                    }
                    steps {
                        script {
                            def imageTag = env.VERSION_MAP['teach-bleats-backend']
                            def ecrRepo = "${env.ECR_REGISTRY}/teach-bleats-backend"

                            echo "Building Backend Image: ${ecrRepo}:${imageTag}"

                            sh """
                                cd backend
                                docker build -t backend .
                                docker tag backend:${imageTag} ${ecrRepo}:${imageTag}
                                docker push ${ecrRepo}:${imageTag}
                            """
                        }
                    }
                }

                stage('Build & Push Cache') {
                    when {
                        expression { env.BUILD_CACHE == "true" }
                    }
                    steps {
                        script {
                            def imageTag = env.VERSION_MAP['teach-bleats-cache']
                            def ecrRepo = "${env.ECR_REGISTRY}/teach-bleats-cache"

                            echo "Building Cache Image: ${ecrRepo}:${imageTag}"

                            sh """
                                cd cache
                                docker build -t cache .
                                docker tag cache:${imageTag} ${ecrRepo}:${imageTag}
                                docker push ${ecrRepo}:${imageTag}
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Docker images built & pushed to AWS ECR successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}

