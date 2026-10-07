// =============================================================================
// DevSecOps pipeline (Jenkins, declarative)
// Order: cheap and fast checks first, expensive ones last (fail early).
//   1. Secrets      -> Gitleaks      (blocks on any leak)
//   2. Dependencies -> Trivy fs      (blocks on HIGH / CRITICAL)
//   3. Build        -> Docker image
//   4. Unit tests   -> pytest         (blocks on a failing test)
//   5. SAST         -> Bandit         (blocks on medium+ severity AND confidence)
//   6. SAST         -> SonarQube      (blocks if the quality gate fails)
//   7. Image scan   -> Trivy image    (blocks on HIGH / CRITICAL that have a fix)
//   8. DAST         -> OWASP ZAP      (passive baseline, report only)
//   9. Deploy       -> staging        (only reached if every gate above passed)
// Each scan also writes a JSON/HTML report that is archived with the build.
// =============================================================================

pipeline {
  agent any

  // Automation: Jenkins checks GitHub every ~2 minutes and starts a build
  // when there is a new commit (no manual click needed).
  triggers {
    pollSCM('H/2 * * * *')
  }

  stages {

    // --- Checkout ------------------------------------------------------------
    stage('Checkout') {
      steps {
        deleteDir()
        checkout scm
      }
    }

    // --- 1. Secrets scan -----------------------------------------------------
    stage('Secret scan (Gitleaks)') {
      steps {
        sh '''
          mkdir -p tools
          curl -sL https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz | tar -xz -C tools gitleaks
          ./tools/gitleaks detect --source . --no-git --exit-code 1 --report-path gitleaks-report.json
        '''
      }
    }

    // --- 2. Dependency scan (SCA) --------------------------------------------
    stage('Dependency and config scan (Trivy)') {
      steps {
        sh '''
          curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ./tools
          ./tools/trivy fs --format json --output trivy-fs-report.json --exit-code 0 --severity HIGH,CRITICAL .
          ./tools/trivy fs --exit-code 1 --severity HIGH,CRITICAL .
        '''
      }
    }

    // --- 3. Build ------------------------------------------------------------
    stage('Build Docker image') {
      steps {
        sh 'docker build -t vulnerable-app:${BUILD_NUMBER} .'
      }
    }

    // --- 4. Unit tests -------------------------------------------------------
    // Tests remain outside the Docker image because .dockerignore excludes tests/.
    // --volumes-from jenkins exposes the Jenkins workspace to the test container.
    stage('Unit tests (pytest)') {
      steps {
        sh '''
          docker run --rm \
            --user "$(id -u):$(id -g)" \
            --volumes-from jenkins \
            -w "$WORKSPACE" \
            -e PYTHONDONTWRITEBYTECODE=1 \
            vulnerable-app:${BUILD_NUMBER} \
            python -m pytest -q -p no:cacheprovider tests
        '''
      }
    }

    // --- 5. SAST (Bandit) ----------------------------------------------------
    stage('SAST (Bandit)') {
      steps {
        sh '''
          docker run --rm vulnerable-app:${BUILD_NUMBER} sh -c "pip install -q bandit >/dev/null 2>&1 && bandit -r /app/app.py -f json" > bandit-report.json || true
          docker run --rm vulnerable-app:${BUILD_NUMBER} sh -c "pip install -q bandit >/dev/null 2>&1 && bandit -r /app/app.py -ll -ii"
        '''
      }
    }

    // --- 6. SAST (SonarQube) -------------------------------------------------
    stage('SAST (SonarQube)') {
      steps {
        withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
          sh '''
            docker run --rm \
              --user "$(id -u):$(id -g)" \
              --network devsecops-net \
              --volumes-from jenkins \
              -w "$WORKSPACE" \
              -e SONAR_TOKEN="$SONAR_TOKEN" \
              -e SONAR_USER_HOME=/tmp/.sonar \
              sonarsource/sonar-scanner-cli \
              -Dsonar.host.url=http://sonarqube:9000 \
              -Dsonar.projectKey=devsecops \
              -Dsonar.projectBaseDir="$WORKSPACE" \
              -Dsonar.sources=app.py \
              -Dsonar.python.version=3.13 \
              -Dsonar.qualitygate.wait=true \
              -Dsonar.qualitygate.timeout=300
          '''
        }
      }
    }

    // --- 7. Docker image scan -----------------------------------------------
    // --ignore-unfixed means only vulnerabilities with an available fix
    // can block the pipeline.
    stage('Docker image scan (Trivy)') {
      steps {
        sh '''
          ./tools/trivy image \
            --ignore-unfixed \
            --format json \
            --output trivy-image-report.json \
            --exit-code 0 \
            --severity HIGH,CRITICAL \
            vulnerable-app:${BUILD_NUMBER}

          ./tools/trivy image \
            --ignore-unfixed \
            --exit-code 1 \
            --severity HIGH,CRITICAL \
            vulnerable-app:${BUILD_NUMBER}
        '''
      }
    }

    // --- 8. DAST (OWASP ZAP baseline) ---------------------------------------
    stage('DAST (OWASP ZAP baseline)') {
      steps {
        sh '''
          docker network create dast-net-${BUILD_NUMBER}

          docker run -d \
            --name dast-app-${BUILD_NUMBER} \
            --network dast-net-${BUILD_NUMBER} \
            --network-alias target \
            vulnerable-app:${BUILD_NUMBER}

          sleep 8

          docker run \
            --name zap-${BUILD_NUMBER} \
            --network dast-net-${BUILD_NUMBER} \
            --user root \
            zaproxy/zap-stable \
            sh -c "mkdir -p /zap/wrk && zap-baseline.py -t http://target:5000 -r zap-report.html -I" || true

          docker cp zap-${BUILD_NUMBER}:/zap/wrk/zap-report.html zap-report.html
          test -f zap-report.html
        '''
      }

      post {
        always {
          sh '''
            docker rm -f dast-app-${BUILD_NUMBER} zap-${BUILD_NUMBER} || true
            docker network rm dast-net-${BUILD_NUMBER} || true
          '''
        }
      }
    }

    // --- 9. Deploy to staging ------------------------------------------------
    stage('Deploy (staging)') {
      steps {
        sh '''
          docker rm -f staging-app || true
          docker run -d \
            --name staging-app \
            -p 5000:5000 \
            vulnerable-app:${BUILD_NUMBER}
        '''
      }
    }
  }

  // --- Post-build actions ----------------------------------------------------
  post {

    // Archive security reports even if a security gate fails.
    always {
      archiveArtifacts \
        artifacts: 'gitleaks-report.json, trivy-fs-report.json, bandit-report.json, trivy-image-report.json, zap-report.html', \
        allowEmptyArchive: true
    }

    // Send an email when the pipeline is blocked.
    failure {
      echo "PIPELINE BLOCKED on build ${env.BUILD_NUMBER}: a security gate failed. See the console of the red stage."

      emailext(
        to: 'Insaf.Torkhani@Esprit.tn',
        subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
        body: """The DevSecOps pipeline has FAILED.

Job: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
Status: FAILED

A security gate failed. Check Jenkins for the failed stage and console output.

Jenkins: ${env.BUILD_URL}
"""
      )
    }

    // Send an email when everything passes.
    success {
      echo "All security gates passed on build ${env.BUILD_NUMBER}."
      echo "SonarQube dashboard: http://localhost:9000/dashboard?id=devsecops"

      emailext(
        to: 'Insaf.Torkhani@Esprit.tn',
        subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
        body: """The DevSecOps pipeline completed successfully.

Job: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
Status: SUCCESS

All security gates passed.

Jenkins: ${env.BUILD_URL}
SonarQube: http://localhost:9000/dashboard?id=devsecops
"""
      )
    }
  }
}