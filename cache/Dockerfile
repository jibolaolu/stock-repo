# Step 1: Use an official Maven image to build the application
FROM maven:3.8.6-openjdk-11 as build

# Set the working directory in the container
WORKDIR /app

# Copy the pom.xml and install the dependencies (this helps with caching)
COPY pom.xml .

# Download dependencies without copying the entire source
RUN mvn dependency:go-offline

# Copy the source code into the container
COPY src /app/src

# Package the application into a jar file
RUN mvn clean package -DskipTests

# Step 2: Use a JDK-based image to run the app
FROM openjdk:11-jre-slim

# Set the working directory in the container
WORKDIR /app

# Copy the jar file from the build stage to the container
COPY --from=build /app/target/stock-cache-0.0.1-SNAPSHOT.jar /app/stock-cache.jar

# Expose the port the application runs on
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "/app/stock-cache.jar"]
