// RAR 17.08.25 Check Case Closure if all Workflow Items are completed
// RAR 18.09.25 Added rollback functionality using GroovyRollbackException to prevent save when open tasks exist --> customer does not want to prevent saving, therefore commented
// RAR 18.09.25 Added Verify transmissionEnvelope

import ch.ategra.ceam.GroovyRollbackException

if (mainEntity == null) { return }
def caseEntity = mainEntity

def printLogStatements = true;
def printLogPrefix = "Skript ZHVDAFM-Verifizierung-PTLG-Geschaeft: ";
if (printLogStatements) println(printLogPrefix + "Skriptausführung gestartet");

def isPTLGSchalter = caseEntity.getSystemName() == "PTLGSchalter"

def caseStatus = caseEntity.getFieldValue("status")
if (caseStatus != "Completed") {
    return
}

// Verify if a workflow item is open 
def workflowItems = gt.getWorkflowController().getWorkflowActionItemsByParentEntity(caseEntity)
def openWorkflowItems = workflowItems.find { item ->
    def status = item.getFieldValue("status")
    status != "Completed" && status != "NotRelevant"
}

// Verify if a transmissionEnvelope contains "Registration"
def transmissionEnvelopes = gt.getTransmissionEnvelopeController().getTransmissionEnvelopesByAssociatedCase(caseEntity)
println "transmissionEnvelops:" + transmissionEnvelopes
def validTransmissionEnvelope = transmissionEnvelopes.find { item -> 
    item.getFieldValue("title")?.toLowerCase()?.contains("registration")
}

if (openWorkflowItems) {
    resultObject.addErrorMessage("Das Geschäft kann nicht auf 'Erledigt' gesetzt werden, " +
            "da es noch offene Workflow-Aufgaben gibt. Bitte schliessen Sie zuerst alle Workflow-Aufgaben ab.")
    
    // Suppress the save success message
    //resultObject.setFailure()
    
    // Throw exception to rollback the entire save operation
    //throw new GroovyRollbackException()
}

if (isPTLGSchalter) {
    resultObject.addWarningMessage("Bitte jetzt prüfen, ob eine E-Mail an den Gesuchstellenden zugestellt wurde.")
}

if (!validTransmissionEnvelope && !isPTLGSchalter) {
    resultObject.addErrorMessage("Das Geschäft kann nicht auf 'Erledigt' gesetzt werden, " +
        "weil kein Übermittlungskuvert vorhanden ist für Registration abgelehnt oder Registration erfolgreich abgeschlossen.")
}
