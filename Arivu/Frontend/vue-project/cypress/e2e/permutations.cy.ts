describe('Settings Permutations', () => {
    const TEST_KEY = Cypress.env('OPENAI_API_KEY') || 'your-key-here' // Masked for safety

    // Matrix
    const embeddings = [
        { name: 'Local', value: 'local:all-MiniLM-L6-v2' },
        { name: 'OpenAI', value: 'openai:text-embedding-3-small' }
    ]
    const models = [
        { name: 'OpenAI', value: 'gpt-4o-mini' },
        { name: 'Ollama', value: 'llama3' }
    ]
    const rerankings = [false, true] // Off, On

    // Iterate
    embeddings.forEach(emb => {
        models.forEach(model => {
            rerankings.forEach(rerank => {

                const scenarioName = `Emb:${emb.name} | Model:${model.name} | Rerank:${rerank ? 'On' : 'Off'}`

                it(scenarioName, () => {
                    const timestamp = Date.now()
                    const projectName = `AutoTest_${emb.name}_${model.name}_${rerank ? 'R' : ''}_${timestamp}`

                    cy.visit('/')
                    cy.contains('New project', { timeout: 15000 }).click()

                    // 1. Create Project
                    cy.get('input[placeholder="Project name"]').type(projectName)

                    // Select Embedding Model in Modal
                    cy.contains('label', 'Embedding Model').next().find('select').select(emb.value)
                    cy.contains('button', 'Create').click()

                    // Verify Project Active
                    cy.contains(projectName, { timeout: 15000 }).should('exist')

                    // 2. Configure Settings
                    cy.contains('Settings').click()

                    // Embedding API Key (If OpenAI)
                    if (emb.name !== 'Local') {
                        cy.contains('Advanced Ingestion Settings').click()
                        cy.get('#embeddingApiKey').should('be.visible').clear().type(TEST_KEY)
                    }

                    // Model
                    cy.get('#model').select(model.value)

                    // Chat API Key (If OpenAI)
                    if (model.name === 'OpenAI') {
                        cy.get('#apiKey').should('be.visible').clear().type(TEST_KEY)
                    }

                    // Reranking
                    if (rerank) {
                        cy.get('#enableReranking').click()
                    }

                    // Save
                    cy.contains('Save Settings').click()
                    cy.contains('Settings saved').should('be.visible')

                    // 3. Upload File
                    cy.contains('Documents').click()
                    cy.get('input[type=file]').selectFile('cypress/fixtures/test_doc.txt', { force: true })

                    // Wait for upload & ingestion
                    cy.contains('test_doc.txt', { timeout: 15000 }).should('be.visible')

                    // Wait for status "Indexed" (Capitalized in UI)
                    cy.get('table').contains('Indexed', { timeout: 60000 }).should('be.visible')

                    // 4. Chat
                    cy.contains('Chat').click()
                    cy.get('textarea[placeholder="Ask a question…"]').type('What is the capital of France?{enter}')

                    // 5. Verify Response
                    cy.contains('Paris', { timeout: 60000 }).should('be.visible')
                })
            })
        })
    })
})
