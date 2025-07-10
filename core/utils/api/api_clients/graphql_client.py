from gql import gql, Client
import requests
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
import os # For loading .graphql files
import logging

logger = logging.getLogger(__name__)
# Basic logging config, can be removed if your framework has a central logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Define the base path for .graphql files if you store them externally
# This assumes 'graphql_operations' is a sibling to 'api_clients' under 'helpers'
OPERATIONS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'graphql_operations')


class GraphQLClient:
    def __init__(self, endpoint, auth_token=None, headers=None):
        if not endpoint:
            logger.critical("GraphQL endpoint must be provided for GraphQLClient initialization.")
            raise ValueError("GraphQL endpoint must be provided.")

        self._headers = headers or {}
        if auth_token:
            self._headers["Authorization"] = f"Bearer {auth_token}"
        
        self.endpoint = endpoint
        self.transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=self._headers,
            verify=True,  # Set to False if using self-signed certs (not recommended for prod)
            retries=3,
            timeout=30 # Default timeout for requests
        )
        # fetch_schema_from_transport=False is generally safer for test automation
        # unless you specifically need to validate against the live schema frequently.
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)
        logger.info(f"GraphQLClient initialized for endpoint: {self.endpoint}")

    def execute(self, query_or_mutation_string, variables=None):
        """
        Executes a GraphQL query or mutation.

        :param query_or_mutation_string: The GraphQL query/mutation as a string.
        :param variables: A dictionary of variables for the query/mutation.
        :return: The result from the GraphQL server as a dictionary.
        :raises TransportQueryError: If GraphQL returns errors in the 'errors' field of the response,
                                     or if there's a transport-level error (e.g. non-200 HTTP status).
        :raises Exception: For other unexpected errors during execution.
        """
        try:
            query = gql(query_or_mutation_string) # Validate the query/mutation syntax
            logger.debug(f"Executing GraphQL operation (first 100 chars): {query_or_mutation_string[:100]}... Variables: {variables}")
            
            result = self.client.execute(query, variable_values=variables)
            logger.debug(f"GraphQL result: {result}")
            
            # The gql client's default behavior with RequestsHTTPTransport might raise TransportQueryError
            # for responses that include an 'errors' key, even if HTTP status is 200.
            # If it doesn't, and you want to ensure any GraphQL error is an exception:
            if isinstance(result, dict) and 'errors' in result and result['errors']:
                logger.error(f"GraphQL operation returned errors in response body: {result['errors']}")
                # Re-raise as TransportQueryError or a custom exception for consistency
                raise TransportQueryError(f"GraphQL errors: {result['errors']}", errors=result['errors'], data=result.get('data'))
            
            return result
        except TransportQueryError as tqe:
            # This can be raised by client.execute for HTTP errors or if server returns an 'errors' payload
            # depending on GQL client version and transport behavior.
            logger.error(f"GraphQL TransportQueryError during execution: {tqe}. Response data (if any): {tqe.data}")
            # Consider what to do with tqe.data or tqe.errors if needed
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"GraphQL ConnectionError for endpoint {self.endpoint}: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"GraphQL Timeout for endpoint {self.endpoint}: {timeout_err}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during GraphQL execution: {e.__class__.__name__} - {e}")
            raise

    @staticmethod
    def load_operation_from_file(file_path_relative_to_operations_dir):
        """
        Loads a GraphQL query or mutation from a .graphql file.
        The path is relative to the OPERATIONS_BASE_DIR.
        Example: load_operation_from_file("mutations/create_user.graphql")
        """
        full_path = os.path.join(OPERATIONS_BASE_DIR, file_path_relative_to_operations_dir)
        logger.debug(f"Attempting to load GraphQL operation from file: {full_path}")
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            logger.debug(f"Successfully loaded GraphQL operation from: {full_path}")
            return content
        except FileNotFoundError:
            logger.error(f"GraphQL operation file not found: {full_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading GraphQL operation file {full_path}: {e}")
            raise

# Example Usage (for testing this client directly)
if __name__ == '__main__':
    # This is a placeholder endpoint. Replace with a public GraphQL API for testing if needed.
    # For example, the SpaceX GraphQL API: https://spacex-production.up.railway.app/
    # Or use your actual endpoint from config if available and .env is set up
    from config.settings import env_config # For testing with your configured endpoint
    
    # Use the configured endpoint if available, otherwise a public test one
    TEST_ENDPOINT = env_config.GRAPHQL_ENDPOINT if env_config.GRAPHQL_ENDPOINT != "http://your-app-domain.com/graphql" else "https://spacex-production.up.railway.app/"
    
    if TEST_ENDPOINT:
        logger.info(f"Testing GraphQLClient with endpoint: {TEST_ENDPOINT}")
        try:
            # Example for an unauthenticated endpoint or one where token is optional for some queries
            client = GraphQLClient(endpoint=TEST_ENDPOINT) 
            
            # Example query (specific to SpaceX API if using that as TEST_ENDPOINT)
            example_query_spacex = """
                query ExampleSpaceXQuery {
                  company {
                    name
                    ceo
                    employees
                  }
                }
            """
            # Example query for a generic placeholder if not using SpaceX
            example_query_generic = """
                query HealthCheck {
                    health # Replace with an actual simple query from your schema
                }
            """
            
            # Choose query based on endpoint
            query_to_test = example_query_spacex if "spacex" in TEST_ENDPOINT.lower() else example_query_generic

            if "health" in query_to_test and "spacex" not in TEST_ENDPOINT.lower():
                 logger.info("\nNote: The generic 'health' query is a placeholder. " \
                       "Replace with a valid simple query from your schema for a meaningful test.")
            
            logger.info(f"\nExecuting example query against {TEST_ENDPOINT}...")
            result = client.execute(query_to_test)
            logger.info("\nExample Query Result:", result)

            # Example of loading from a dummy file (if you create it)
            # Create 'helpers/graphql_operations/queries/get_example.graphql' with the query_to_test content
            # Make sure the OPERATIONS_BASE_DIR is correctly pointing to 'helpers/graphql_operations'
            # To test this part, you would manually create the file and directory.
            # For example:
            # helpers/graphql_operations/queries/get_example.graphql
            # containing:
            # query ExampleQueryFromFile { company { name ceo } } # if using SpaceX
            
            # print("\nAttempting to load and execute query from file...")
            # try:
            #     # Adjust the path if your example file is different
            #     query_from_file_str = GraphQLClient.load_operation_from_file("queries/get_example.graphql")
            #     result_from_file = client.execute(query_from_file_str)
            #     print("Result from file query:", result_from_file)
            # except FileNotFoundError:
            #     print("Skipping 'load from file' test: Example .graphql file not found in expected location " \
            #           "(e.g., helpers/graphql_operations/queries/get_example.graphql).")
            # except Exception as e_file:
            #     print(f"Could not test loading from file: {e_file}")

        except ValueError as ve:
            logger.error(f"Initialization error: {ve}")
        except TransportQueryError as tqe:
            logger.error(f"GraphQL specific error during execution: {tqe}")
            if tqe.errors:
                logger.error(f"GraphQL errors payload: {tqe.errors}")
            if tqe.data:
                logger.error(f"GraphQL data payload (if any): {tqe.data}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to the GraphQL endpoint: {TEST_ENDPOINT}. Is it running and accessible?")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e.__class__.__name__} - {e}")
    else:
        logger.error("TEST_ENDPOINT not set, and default GraphQL endpoint not configured or placeholder. " \
              "Skipping GraphQLClient example execution.")
