package nova.client;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.web.reactive.function.client.WebClient;

import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest
public class AIServiceClientTest {

    @Autowired
    private AIServiceClient aiServiceClient;

    @MockBean
    private WebClient webClient;

    @Test
    public void contextLoads() {
        assertNotNull(aiServiceClient);
    }
}
