pipeline {
    agent any

    environment {
        SCANNER_HOME = tool 'sonar-scanner'
    }
    
    stages {
        stage('Checkout Code from GitHub') {
            steps {
                // Checkout the GitHub repository
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], 
                userRemoteConfigs: [[url: 'https://github.com/HarryRichard08/web-scrapping.git']]])
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                // Run SonarQube analysis using the configured SonarQube Scanner
                withSonarQubeEnv('sonar-server') {
                    sh """${SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectName=test \
                    -Dsonar.projectKey=test"""
                }
            }
        }
        
        stage('Compare CSV Files') {
            steps {
                script {
                    // Read the contents of the predicted.csv and actual.csv files from the Git repository
                    def predictedFile = readFileFromGit('output/predicted.csv')
                    def actualFile = readFileFromGit('output/actual.csv')

                    // Compare the contents of the CSV files
                    if (predictedFile == actualFile) {
                        echo 'CSV files are identical. Proceeding with file copy.'
                    } else {
                        error 'CSV files are different. Skipping file copy.'
                    }
                }
            }
        }

        stage('Read VM Details') {
            steps {
                script {
                    // Read the VM details JSON file from the Git repository
                    def vmDetails = readJSON file: 'vm_details/vm_details.json'
                    currentBuild.description = "Moving 'scrape.py' to ${vmDetails.host}"
                    stash includes: 'scrape.py', name: 'scrapeStash'
                }
            }
        }

        stage('Copy File to Remote Server') {
            steps {
                // Unstash the 'scrape.py' file
                unstash 'scrapeStash'

                script {
                    def vmDetails = readJSON file: 'vm_details/vm_details.json'

                    // Use VM details in this step
                    def remoteHost = vmDetails.host
                    def remoteUsername = vmDetails.username
                    def remotePassword = vmDetails.password

                    // Specify the full path to sshpass
                    def sshpassPath = '/usr/bin/sshpass' // Use the correct path on your system

                    // Use sshpass to copy the file from Jenkins workspace to the remote server
                    sh "${sshpassPath} -p '${remotePassword}' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null scrape.py ${remoteUsername}@${remoteHost}:/root/airflow/dags/"
                }
            }
        }
    }
}

def readFileFromGit(filePath) {
    return sh(script: "git show origin/main:${filePath}", returnStdout: true).trim()
}
