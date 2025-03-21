
// pipeline {
//     agent {
//         docker {
//             image 'jibolaolu/jenkins-agent:latest'
//             args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
//         }
//     }
//
//     environment {
//         AWS_REGION = 'eu-west-2'
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
//                     sh "git status"
//                 }
//             }
//         }
//
//         stage('Get Latest Version from ECR') {
//             steps {
//                 script {
//                     def repoNames = ['teach-bleats-frontend', 'teach-bleats-backend', 'teach-bleats-cache']
//
//                     env.VERSION_MAP = [:]
//
//                     for (repo in repoNames) {
//                         def lastTag = sh(script: """
//                             aws ecr describe-images --repository-name ${repo} --region ${AWS_REGION} \
//                             --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' --output text 2>/dev/null || echo "none"
//                         """, returnStdout: true).trim()
//
//                         def newVersion = "1.0.0"
//                         if (lastTag != "none") {
//                             def parts = lastTag.tokenize('.')
//                             if (parts.size() == 3) {
//                                 parts[2] = (parts[2].toInteger() + 1).toString()
//                                 newVersion = parts.join('.')
//                             }
//                         }
//
//                         env.VERSION_MAP[repo] = newVersion
//                         echo "Repo ${repo} new version: ${newVersion}"
//                     }
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
//             steps {
//                 withCredentials([[
//                     $class: 'AmazonWebServicesCredentialsBinding',
//                     credentialsId: 'aws_credentials',
//                     accessKeyVariable: 'AWS_ACCESS_KEY_ID',
//                     secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
//                 ]]) {
//                     script {
//                         echo '🔐 Logging into AWS ECR...'
//                         sh """
//                             export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
//                             export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY
//                             export HOME=\$WORKSPACE
//                             mkdir -p \$WORKSPACE/.docker
//                             aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin --config \$WORKSPACE/.docker ${env.ECR_REGISTRY}
//                         """
//                     }
//                 }
//             }
//         }
//
//         stage('Build & Push Docker Images') {
//             parallel {
//                 stage('Build & Push Frontend') {
//                     when {
//                         expression { env.BUILD_FRONTEND == "true" }
//                     }
//                     steps {
//                         script {
//                             def imageTag = env.VERSION_MAP['teach-bleats-frontend']
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
//                             def imageTag = env.VERSION_MAP['teach-bleats-backend']
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
//                             def imageTag = env.VERSION_MAP['teach-bleats-cache']
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
//             echo "✅ Docker images built & pushed to AWS ECR successfully!"
//         }
//         failure {
//             echo "❌ Pipeline failed!"
//         }
//     }
// }
//

// pipeline {
//     agent {
//         docker {
//             image 'jibolaolu/jenkins-agent:latest'
//             args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
//         }
//     }
//
//     environment {
//         AWS_REGION = 'eu-west-2'
//         FRONTEND_VERSION = ''
//         BACKEND_VERSION = ''
//         CACHE_VERSION = ''
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
//                         env.AWS_ACCOUNT_ID = sh(script: "aws sts get-caller-identity --query 'Account' --output text", returnStdout: true).trim()
//                         env.ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
//                         echo "✅ AWS Account ID: ${env.AWS_ACCOUNT_ID}"
//                     }
//                 }
//             }
//         }
//
//         stage('Checkout Code') {
//             steps {
//                 checkout([$class: 'GitSCM',
//                     branches: [[name: '*/master']],
//                     extensions: [[$class: 'WipeWorkspace']],
//                     userRemoteConfigs: [[
//                         credentialsId: 'github-credentials',
//                         url: 'https://github.com/jibolaolu/stock-repo.git'
//                     ]]
//                 ])
//             }
//         }
//
//         stage('Detect Changes') {
//             steps {
//                 script {
//                     def changedFiles = sh(script: "git diff --name-only HEAD^ HEAD", returnStdout: true).trim().split("\n")
//                     echo "🧾 Changed Files: ${changedFiles}"
//
//                     env.BUILD_FRONTEND = changedFiles.any { it.startsWith("frontend/") || it == "Dockerfile" || it == ".env" } ? "true" : "false"
//                     env.BUILD_BACKEND  = changedFiles.any { it.startsWith("backend/")  || it == "Dockerfile" || it == ".env" } ? "true" : "false"
//                     env.BUILD_CACHE    = changedFiles.any { it.startsWith("cache/")    || it == "Dockerfile" || it == ".env" } ? "true" : "false"
//                 }
//             }
//         }
//
//         stage('Get Latest Versions') {
//             steps {
//                 script {
//                     if (env.BUILD_FRONTEND == "true") {
//                         def lastFrontend = sh(script: """
//                             aws ecr describe-images --repository-name teach-bleats-frontend --region ${AWS_REGION} \
//                             --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' \
//                             --output text 2>/dev/null || echo none
//                         """, returnStdout: true).trim()
//                         env.FRONTEND_VERSION = (lastFrontend == "none") ? "1.0.0" : bumpVersion(lastFrontend)
//                     }
//
//                     if (env.BUILD_BACKEND == "true") {
//                         def lastBackend = sh(script: """
//                             aws ecr describe-images --repository-name teach-bleats-backend --region ${AWS_REGION} \
//                             --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' \
//                             --output text 2>/dev/null || echo none
//                         """, returnStdout: true).trim()
//                         env.BACKEND_VERSION = (lastBackend == "none") ? "1.0.0" : bumpVersion(lastBackend)
//                     }
//
//                     if (env.BUILD_CACHE == "true") {
//                         def lastCache = sh(script: """
//                             aws ecr describe-images --repository-name teach-bleats-cache --region ${AWS_REGION} \
//                             --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' \
//                             --output text 2>/dev/null || echo none
//                         """, returnStdout: true).trim()
//                         env.CACHE_VERSION = (lastCache == "none") ? "1.0.0" : bumpVersion(lastCache)
//                     }
//                 }
//             }
//         }
//
//         stage('Login to AWS ECR') {
//             steps {
//                 withCredentials([[
//                     $class: 'AmazonWebServicesCredentialsBinding',
//                     credentialsId: 'aws_credentials',
//                     accessKeyVariable: 'AWS_ACCESS_KEY_ID',
//                     secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
//                 ]]) {
//                     script {
//                         sh """
//                             export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
//                             export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY
//                             export HOME=\$WORKSPACE
//                             aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}
//                         """
//                     }
//                 }
//             }
//         }
//
//         stage('Build & Push Docker Images') {
//             parallel {
//                 stage('Build & Push Frontend') {
//                     when { expression { env.BUILD_FRONTEND == "true" } }
//                     steps {
//                         script {
//                             def tag = env.FRONTEND_VERSION
//                             def repo = "${env.ECR_REGISTRY}/teach-bleats-frontend"
//                             sh """
//                                 cd frontend
//                                 docker build -t frontend .
//                                 docker tag frontend:latest ${repo}:${tag}
//                                 docker push ${repo}:${tag}
//                             """
//                         }
//                     }
//                 }
//
//                 stage('Build & Push Backend') {
//                     when { expression { env.BUILD_BACKEND == "true" } }
//                     steps {
//                         script {
//                             def tag = env.BACKEND_VERSION
//                             def repo = "${env.ECR_REGISTRY}/teach-bleats-backend"
//                             sh """
//                                 cd backend
//                                 docker build -t backend .
//                                 docker tag backend:latest ${repo}:${tag}
//                                 docker push ${repo}:${tag}
//                             """
//                         }
//                     }
//                 }
//
//                 stage('Build & Push Cache') {
//                     when { expression { env.BUILD_CACHE == "true" } }
//                     steps {
//                         script {
//                             def tag = env.CACHE_VERSION
//                             def repo = "${env.ECR_REGISTRY}/teach-bleats-cache"
//                             sh """
//                                 cd cache
//                                 docker build -t cache .
//                                 docker tag cache:latest ${repo}:${tag}
//                                 docker push ${repo}:${tag}
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
//             echo "✅ Docker images built & pushed successfully."
//         }
//         failure {
//             echo "❌ Pipeline failed."
//         }
//     }
// }
//
// def bumpVersion(String version) {
//     def parts = version.tokenize('.')
//     if (parts.size() == 3) {
//         parts[2] = (parts[2].toInteger() + 1).toString()
//         return parts.join('.')
//     }
//     return "1.0.0"
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
        ECR_ACCOUNT_ID = credentials('aws-account-id') // Securely fetch from Jenkins
        ECR_REGISTRY = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        HOME = "${env.WORKSPACE}"
    }

     options {
        buildDiscarder(logRotator(
            daysToKeepStr: '7',
            numToKeepStr: '5',
            artifactDaysToKeepStr: '3',
            artifactNumToKeepStr: '2'
        ))
    }

    stages {
        stage('Set AWS Context') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws_credentials',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                ]]) {
                    script {
                        env.AWS_ACCOUNT_ID = sh(
                            script: "aws sts get-caller-identity --query 'Account' --output text",
                            returnStdout: true
                        ).trim()
                        env.ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                    }
                }
            }
        }

        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/master']],
                    extensions: [[$class: 'WipeWorkspace']],
                    userRemoteConfigs: [[
                        credentialsId: 'github-credentials',
                        url: 'https://github.com/jibolaolu/stock-repo.git'
                    ]]
                ])
            }
        }

        stage('Detect Changes') {
            steps {
                script {
                    def changes = sh(script: "git diff --name-only HEAD^ HEAD", returnStdout: true).trim().split("\n")
                    env.BUILD_FRONTEND = changes.any { it.startsWith("frontend/") } ? "true" : "false"
                    env.BUILD_BACKEND  = changes.any { it.startsWith("backend/") } ? "true" : "false"
                    env.BUILD_CACHE    = changes.any { it.startsWith("cache/") } ? "true" : "false"

                    if (env.BUILD_FRONTEND == "false" && env.BUILD_BACKEND == "false" && env.BUILD_CACHE == "false") {
                        env.BUILD_FRONTEND = env.BUILD_BACKEND = env.BUILD_CACHE = "true"
                        echo "No changes detected – forcing initial build of all components."
                    }
                }
            }
        }

        stage('Determine Versions') {
            steps {
                script {
                    def repos = [
                        [name: "teach-bleats-frontend", build: env.BUILD_FRONTEND],
                        [name: "teach-bleats-backend",  build: env.BUILD_BACKEND],
                        [name: "teach-bleats-cache",    build: env.BUILD_CACHE]
                    ]

                    repos.each { repo ->
                        if (repo.build == "true") {
                            def latestTag = sh(
                                script: """
                                    aws ecr describe-images --repository-name ${repo.name} \
                                    --region ${AWS_REGION} \
                                    --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' \
                                    --output text 2>/dev/null || echo none
                                """,
                                returnStdout: true
                            ).trim()

                            def newVersion = (latestTag == "none") ? "1.0.0" : bumpVersion(latestTag)

                            if (repo.name.contains("frontend")) {
                                env.FRONTEND_VERSION = newVersion
                            } else if (repo.name.contains("backend")) {
                                env.BACKEND_VERSION = newVersion
                            } else if (repo.name.contains("cache")) {
                                env.CACHE_VERSION = newVersion
                            }

                            echo "📦 ${repo.name} => New Version: ${newVersion}"
                        }
                    }
                }
            }
        }

        stage('Login to ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws_credentials',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                ]]) {
                    sh """
                        export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY
                        export HOME=\$WORKSPACE
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    """
                }
            }
        }

        stage('Build & Push Images') {
            parallel {
                stage('Frontend') {
                    when { expression { env.BUILD_FRONTEND == "true" } }
                    steps {
                        script {
                            def tag = env.FRONTEND_VERSION
                            def repo = "${env.ECR_REGISTRY}/teach-bleats-frontend"
                            sh """
                                export HOME=\$WORKSPACE
                                cd frontend
                                docker build -t frontend .
                                docker tag frontend:latest ${repo}:${tag}
                                docker push ${repo}:${tag}
                            """
                        }
                    }
                }

                stage('Backend') {
                    when { expression { env.BUILD_BACKEND == "true" } }
                    steps {
                        script {
                            def tag = env.BACKEND_VERSION
                            def repo = "${env.ECR_REGISTRY}/teach-bleats-backend"
                            sh """
                                export HOME=\$WORKSPACE
                                cd backend
                                docker build -t backend .
                                docker tag backend:latest ${repo}:${tag}
                                docker push ${repo}:${tag}
                            """
                        }
                    }
                }

                stage('Cache') {
                    when { expression { env.BUILD_CACHE == "true" } }
                    steps {
                        script {
                            def tag = env.CACHE_VERSION
                            def repo = "${env.ECR_REGISTRY}/teach-bleats-cache"
                            sh """
                                export HOME=\$WORKSPACE
                                cd cache
                                docker build -t cache .
                                docker tag cache:latest ${repo}:${tag}
                                docker push ${repo}:${tag}
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ All Docker images built and pushed successfully."
        }
        failure {
            echo "❌ Build failed. Check logs for more info."
        }
    }
}

def bumpVersion(version) {
    def parts = version.tokenize('.')
    if (parts.size() == 3) {
        parts[2] = (parts[2] as int) + 1
        return "${parts[0]}.${parts[1]}.${parts[2]}"
    } else {
        return "1.0.0"
    }
}
