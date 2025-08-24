
from jinja2 import Template

TEMPLATE = Template(r'''
pipeline {
  agent any

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
        sh 'docker run --rm -v $WORKSPACE:/src -v $WORKSPACE/reports:/report owasp/dependency-check --project {{ project_name }} --scan /src --out /report --format ALL'
      }
    }
    stage('Trivy') {
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
    stage('Publish Reports') {
      steps {
        archiveArtifacts artifacts: 'reports/**/*.*', fingerprint: true
      }
    }
  }
}
'''.strip())

def generate_jenkinsfile(github_url: str, sonar_url: str):
    return TEMPLATE.render(github_url=github_url, sonar_url=sonar_url, project_name='cast-autosec')
