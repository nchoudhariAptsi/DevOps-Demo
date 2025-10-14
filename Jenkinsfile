pipeline {
    agent any

    stages {
        // stage('Removing old artifacts') {
        //     steps {
        //         echo "Removing old artifacts"
        //         //sh "rm -rf ~/.m2/repository"
        //     }
        //     post {
        //         success {
        //             script {
        //                 input(id: 'ProceedRemoving', message: 'Removing old artifacts. Proceed to static code analysis?', ok: 'Proceed')
        //             }
        //         }
        //         always {
        //             echo 'Removing old artifacts stage completed.'
        //         }
        //         failure {
        //             echo 'Removing old artifacts stage failed.'
        //         }
        //     }
        // }

        stage('Static Analysis') {
            steps {
                echo "Running Checkstyle"
                bat "mvn checkstyle:checkstyle"
                
                echo "Running PMD"
                bat "mvn pmd:pmd"
                
                echo "Running SpotBugs"
                bat "mvn spotbugs:spotbugs"
            }
            post {
                always {
                    // Archive the reports
                    archiveArtifacts artifacts: 'target/checkstyle-result.xml, target/pmd.xml, target/spotbugs.xml', allowEmptyArchive: true
                    echo 'Static analysis reports archived.'
                }
                success {
                    script {
                        input(id: 'ProceedStaticAnalysis', message: 'Static analysis completed. Parse and generate reports?', ok: 'Proceed')
                    }
                }
                failure {
                    emailext(subject: 'Pipeline Failed', body: 'Static analysis stage failed. Please check the Jenkins logs.', to: 'your-email@example.com')
                    echo 'Static analysis stage failed.'
                    error('Static analysis failed. Pipeline aborted.')
                }
            }
        }
        
        stage('Parse and Generate Report') {
            steps {
                script {
                    // Use python3 if that's the installed version
                    bat 'python3 parse_sastTools.py'
                    
                    // Optionally, archive the generated CSV file
                    archiveArtifacts artifacts: 'sasttools_summary.csv', allowEmptyArchive: true
                }
            }
            post {
                always {
                    echo 'Parse and generate report stage completed.'
                }
                success {
                    script {
                        input(id: 'ProceedParse', message: 'Parse and generate report completed. Proceed to Build?', ok: 'Proceed')
                    }
                }
                failure {
                    echo 'Parse and generate report failed.'
                }
            }
        }
        
        stage('Build') {
            steps {
                echo "Code building"
                bat "mvn clean package"
            }
            post {
                always {
                    echo 'Build stage completed.'
                }
                success {
                    script {
                        input(id: 'ProceedBuild', message: 'Build completed. Proceed to Test?', ok: 'Proceed')
                    }
                }
                failure {
                    echo 'Build failed.'
                }
            }
        }
       
        stage('Test') {
            steps {
                echo "Code testing"
                bat "mvn test"
            }
            post {
                always {
                    echo 'Test stage completed.'
                }
                success {
                    script {
                        input(id: 'ProceedTest', message: 'Test completed. Proceed to Generate SBOM?', ok: 'Proceed')
                    }
                }
                failure {
                    echo 'Test failed.'
                }
            }
        }
        stage('OWASP Dependency Check') {
            steps {
                echo "Running OWASP Dependency Check"
                bat '''
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
                    script {
                        input(id: 'ProceedOWASP', message: 'OWASP Dependency Check completed. Proceed to Deployment?', ok: 'Proceed')
                    }
                }
                failure {
                    echo 'OWASP Dependency Check stage failed.'
                }
            }
        }
        stage('Generate SBOM') {
            steps {
                echo "Generating SBOM in CycloneDX format"
                bat '''
                syft . --output cyclonedx=sbom.xml
                '''
                archiveArtifacts artifacts: 'sbom.xml', allowEmptyArchive: false
            }
            post {
                success {
                    script {
                        input(id: 'ProceedSBOM', message: 'SBOM generation completed. Proceed to Scan with Grype?', ok: 'Proceed')
                    }
                }
                always {
                    echo 'Generate SBOM stage completed.'
                }
                failure {
                    echo 'Generate SBOM stage failed.'
                }
            }
        }

        stage('Scan with Grype') {
            steps {
                echo "Scanning SBOM with Grype"
                bat '''
                grype sbom:sbom.xml --output table
                '''
            }
            post {
                success {
                    script {
                        input(id: 'ProceedGrype', message: 'Grype scan completed. Proceed to Deployment?', ok: 'Proceed')
                    }
                }
                always {
                    echo 'Scan with Grype stage completed.'
                }
                failure {
                    echo 'Scan with Grype stage failed.'
                }
            }
        }

        stage('Deployment') {
            steps {
                script {
                    echo "Deploying the application"
                    bat '''
                    cd target
                    if [ -f "javabestpractices-1.0-SNAPSHOT-webservice.jar" ]; then
                        java -jar javabestpractices-1.0-SNAPSHOT-webservice.jar
                    else
                        echo "Error: JAR file not found!"
                        exit 1
                    fi
                    '''
                }
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
