pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'ls -la'
      }
    }

    stage('Secret scan (Gitleaks)') {
      steps {
        sh '''
          mkdir -p tools
          curl -sL https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz | tar -xz -C tools gitleaks
          ./tools/gitleaks detect --source . --no-git --exit-code 1 --report-path gitleaks-report.json
        '''
      }
    }

    stage('Dependency and config scan (Trivy)') {
      steps {
        sh '''
          curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ./tools
          ./tools/trivy fs --exit-code 1 --severity HIGH,CRITICAL .
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh 'docker build -t vulnerable-app:${BUILD_NUMBER} .'
      }
    }

    stage('SAST (Bandit)') {
      steps {
        sh '''
          docker run --rm vulnerable-app:${BUILD_NUMBER} sh -c "pip install -q bandit >/dev/null 2>&1 && bandit -r /app/app.py -f json" > bandit-report.json || true
          docker run --rm vulnerable-app:${BUILD_NUMBER} sh -c "pip install -q bandit >/dev/null 2>&1 && bandit -r /app/app.py -ll -ii"
        '''
      }
    }

    stage('Docker image scan (Trivy)') {
      steps {
        sh '''
          ./tools/trivy image --ignore-unfixed --exit-code 1 --severity HIGH,CRITICAL vulnerable-app:${BUILD_NUMBER}
        '''
      }
    }

    stage('DAST (OWASP ZAP baseline)') {
      steps {
        sh '''
          docker network create dast-net-${BUILD_NUMBER}
          docker run -d --name dast-app-${BUILD_NUMBER} --network dast-net-${BUILD_NUMBER} --network-alias target vulnerable-app:${BUILD_NUMBER}
          sleep 8
          docker run --name zap-${BUILD_NUMBER} --network dast-net-${BUILD_NUMBER} --user root zaproxy/zap-stable sh -c "mkdir -p /zap/wrk && zap-baseline.py -t http://target:5000 -r zap-report.html -I" || true
          docker cp zap-${BUILD_NUMBER}:/zap/wrk/zap-report.html zap-report.html
          test -f zap-report.html
        '''
      }
      post {
        always {
          sh 'docker rm -f dast-app-${BUILD_NUMBER} zap-${BUILD_NUMBER} || true; docker network rm dast-net-${BUILD_NUMBER} || true'
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'gitleaks-report.json, bandit-report.json, zap-report.html', allowEmptyArchive: true
    }
  }
}