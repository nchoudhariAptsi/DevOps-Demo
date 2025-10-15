pipeline {
    agent any

    stages {
        stage('List files') {
            steps {
                sh 'ls -al'
            }
        }
        stage('Static Analysis') {
            steps {
                echo "Running Checkstyle"
                sh "mvn checkstyle:checkstyle"
                
                echo "Running PMD"
                sh "mvn pmd:pmd"
                
                echo "Running SpotBugs"
                sh "mvn spotbugs:spotbugs"
            }
            post {
                always {
                    archiveArtifacts artifacts: 'target/checkstyle-result.xml, target/pmd.xml, target/spotbugs.xml', allowEmptyArchive: true
                    echo 'Static analysis reports archived.'
                }
                success {
                    script {
                        input(id: 'ProceedStaticAnalysis', message: 'Static analysis completed. Parse and generate reports?', ok: 'Proceed')
                    }
                }
                failure {
                    emailext(subject: 'Pipeline Failed', body: 'Static analysis stage failed. Please check Jenkins logs.', to: 'your-email@example.com')
                    error('Static analysis failed. Pipeline aborted.')
                }
            }
        }
        
        stage('Parse and Generate Report') {
            steps {
                sh 'python3 parse_sastTools.py'
                archiveArtifacts artifacts: 'sasttools_summary.csv', allowEmptyArchive: true
            }
            post {
                success {
                    input(id: 'ProceedParse', message: 'Parse and generate report completed. Proceed to Build?', ok: 'Proceed')
                }
            }
        }
        
        stage('Build') {
            steps {
                echo "Code building"
                sh "mvn clean package"
            }
            post {
                success {
                    input(id: 'ProceedBuild', message: 'Build completed. Proceed to Test?', ok: 'Proceed')
                }
            }
        }
       
        stage('Test') {
            steps {
                echo "Code testing"
                sh "mvn test"
            }
            post {
                success {
                    input(id: 'ProceedTest', message: 'Test completed. Proceed to Generate SBOM?', ok: 'Proceed')
                }
            }
        }
        
        stage('OWASP Dependency Check') {
            steps {
                echo "Running OWASP Dependency Check"
                sh '''
                mvn org.owasp:dependency-check-maven:check -Dformat=HTML -DoutputDirectory=dependency-check-report
                mvn org.owasp:dependency-check-maven:check -Dformat=ALL -DoutputDirectory=dependency-check-report
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dependency-check-report/dependency-check-report.html, dependency-check-report/dependency-check-report.txt', allowEmptyArchive: true
                    echo 'OWASP Dependency Check reports archived.'
                }
                success {
                    input(id: 'ProceedOWASP', message: 'OWASP Dependency Check completed. Proceed to Deployment?', ok: 'Proceed')
                }
            }
        }
        
        stage('Generate SBOM') {
            steps {
                echo "Generating SBOM in CycloneDX format"
                sh 'syft . --output cyclonedx=sbom.xml'
                archiveArtifacts artifacts: 'sbom.xml', allowEmptyArchive: false
            }
            post {
                success {
                    input(id: 'ProceedSBOM', message: 'SBOM generation completed. Proceed to Scan with Grype?', ok: 'Proceed')
                }
                always {
                    echo 'Generate SBOM stage completed.'
                }
            }
        }

        stage('Scan with Grype') {
            steps {
                echo "Scanning SBOM with Grype"
                sh 'grype sbom:sbom.xml --output table'
            }
            post {
                success {
                    input(id: 'ProceedGrype', message: 'Grype scan completed. Proceed to Deployment?', ok: 'Proceed')
                }
                always {
                    echo 'Scan with Grype stage completed.'
                }
            }
        }

        stage('Deployment') {
            steps {
                echo "Deploying the application"
                sh '''
                cd target
                if [ -f "javabestpractices-1.0-SNAPSHOT-webservice.jar" ]; then
                    java -jar javabestpractices-1.0-SNAPSHOT-webservice.jar
                else
                    echo "Error: JAR file not found!"
                    exit 1
                fi
                '''
            }
            post {
                always {
                    echo 'Deployment stage completed.'
                }
                success {
                    echo 'Deployment succeeded.'
                }
                failure {
                    echo 'Deployment failed.'
                }
            }
        }
    }
}
