FROM jenkins/jenkins:lts

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    git \
    python3 \
    python3-pip \
    npm \
    openjdk-17-jdk \
    msmtp \
    python3-venv \
    msmtp-mta \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages inside a virtual environment
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir requests pyyaml

# Configure msmtp for email notifications
RUN mkdir -p /etc/msmtp
COPY msmtprc /etc/msmtp/msmtprc
RUN chmod 600 /etc/msmtp/msmtprc && chown jenkins:jenkins /etc/msmtp/msmtprc

# Switch back to Jenkins user
USER jenkins

# Set environment variables for the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install Jenkins plugins for automation
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    git \
    sonar \
    email-ext \
    mailer

# Set Java Home
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
