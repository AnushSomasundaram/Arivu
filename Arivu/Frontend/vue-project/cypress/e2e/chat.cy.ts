describe('Chat View', () => {
    it('loads the chat page', () => {
        cy.visit('/')
        // Should redirect to /chat
        cy.url().should('include', '/chat')

        // Check for static content
        cy.contains('h2', 'Ask Arivu anything')
        cy.get('textarea[placeholder="Ask a question…"]').should('be.visible')
        cy.contains('button', 'Send').should('be.visible')
    })
})
