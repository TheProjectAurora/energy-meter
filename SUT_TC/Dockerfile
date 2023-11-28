# Use an official Tomcat runtime as a parent image
FROM tomcat:latest

# Remove the default ROOT application to replace it with your HTML files and assets
RUN rm -rf /usr/local/tomcat/webapps/ROOT

# Create a new ROOT directory
RUN mkdir /usr/local/tomcat/webapps/ROOT

# Copy your HTML files to the ROOT directory
COPY index.html /usr/local/tomcat/webapps/ROOT/index.html
COPY index2.html /usr/local/tomcat/webapps/ROOT/index2.html

# Copy the entire css, img, and gif folders to the ROOT directory
COPY css /usr/local/tomcat/webapps/ROOT/css
COPY img /usr/local/tomcat/webapps/ROOT/img
COPY gif /usr/local/tomcat/webapps/ROOT/gif

# Optionally, you can expose the Tomcat port (default is 8080)
EXPOSE 8080

