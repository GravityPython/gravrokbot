import logging
import threading

class BotRunner:
    """Base class defining common runner interface"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        self.logger = logging.getLogger("GravRokBot.Runner")
        self.running = False
        self.paused = False
        self.actions = []
        self.interrupt_requested = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start in non-paused state
    
    def add_action(self, action):
        """
        Add an action to the runner
        
        Args:
            action (ActionWorkflow): Action to add
        """
        self.logger.info(f"Adding action: {action.name}")
        self.actions.append(action)
    
    def start(self):
        """Start the runner - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement start()")
    
    def pause(self):
        """Pause the runner"""
        if not self.running:
            self.logger.warning("Cannot pause: runner not running")
            return
            
        if self.paused:
            self.logger.info("Runner already paused")
            return
            
        self.logger.info("Pausing runner")
        self.paused = True
        self.pause_event.clear()
        
    def resume(self):
        """Resume the runner from paused state"""
        if not self.running:
            self.logger.warning("Cannot resume: runner not running")
            return
            
        if not self.paused:
            self.logger.info("Runner already running")
            return
            
        self.logger.info("Resuming runner")
        self.paused = False
        self.pause_event.set()
    
    def wait_if_paused(self):
        """Wait if runner is paused, return True if interrupted while waiting"""
        if not self.paused:
            return False
            
        self.logger.debug("Runner paused, waiting to resume")
        while self.paused and self.running and not self.interrupt_requested:
            # Check for interruption every second
            if not self.pause_event.wait(timeout=1.0):
                if self.interrupt_requested:
                    return True
        
        return self.interrupt_requested
        
    def stop(self):
        """Stop the runner - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement stop()")
    
    def interrupt(self):
        """Request immediate interruption of execution"""
        self.logger.info("Interrupt requested")
        self.interrupt_requested = True
        self.running = False
        self.resume()  # Make sure we're not blocked on pause
    
    def get_action_statuses(self):
        """Get action statuses - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_action_statuses()") 