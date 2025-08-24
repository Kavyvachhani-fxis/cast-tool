pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://localhost:9000'
        SONAR_TOKEN = 'squ_690080621f71ee9419d737f6c43ffb96f18da7a3'
        REPORT_FILE = 'Security_Report.pdf'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: '{{ github_url }}'
            }
        }

        stage('Build') {
            steps {
                sh 'mvn -B -DskipTests clean package || true'
            }
        }

        stage('Dependency-Check') {
            steps {
                sh 'docker run --rm -v $WORKSPACE:/src -v $WORKSPACE/reports:/report owasp/dependency-check --project "cast-autosec" --scan /src --out /report --format ALL'
            }
        }

        stage('Trivy Scan') {
            steps {
                sh 'docker run --rm -v $WORKSPACE:/src -v $WORKSPACE/reports:/out aquasec/trivy fs --security-checks vuln,config --severity HIGH,CRITICAL --format json -o /out/trivy.json /src'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh 'mvn -B -DskipTests sonar:sonar -Dsonar.host.url={{ sonar_url }} || true'
                }
            }
        }

        stage('ZAP Scan') {
            steps {
                sh 'zap-cli quick-scan --self-contained --start-options "-config api.disablekey=true" http://yourapp:8080 || true'
                sh 'zap-cli report -o reports/zap-report.html -f html || true'
            }
        }

        stage('Generate PDF Report') {
            steps {
                script {
                    def reportFile = 'reports/security-report.pdf'
                    sh """
                    python3 <<EOF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas('${reportFile}', pagesize=A4)
c.drawString(100, 800, 'CAST AutoSec - Security Report')

c.drawString(100, 770, '1. SonarQube: See dashboard for details.')
with open('reports/trivy-report.json') as f:
    lines = f.readlines()[:20]
    y = 750
    for line in lines:
        c.drawString(100, y, line.strip())
        y -= 12

c.showPage()
c.save()
EOF
                    """
                }
            }
        }

        stage('Publish Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/**/*.*', fingerprint: true
            }
        }
    }

    post {
        always {
            emailext(
                to: 'd23it180@charusat.edu.in',
                subject: "CAST AutoSec Security Report - Build #${env.BUILD_NUMBER}",
                body: """Hello,

The CAST AutoSec security scan has completed.
Please find attached the generated security report.

Regards,
CAST AutoSec Automation""",
                attachmentsPattern: 'reports/**/*.*',
                mimeType: 'text/html',
                attachLog: true
            )
        }
    }
}
