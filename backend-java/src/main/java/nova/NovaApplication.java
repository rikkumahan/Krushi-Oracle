package nova;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Nova API Gateway - Main Application Entry Point
 * 
 * This Spring Boot application serves as the API gateway for Nova Idea Lab.
 * It handles authentication, routing, and orchestrates calls to the Python AI service.
 */
@SpringBootApplication
public class NovaApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(NovaApplication.class, args);
    }
}
