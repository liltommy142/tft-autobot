"""
learner_scheduler.py - Schedule continuous meta learning

Automatically runs meta analysis at intervals to keep meta database updated.
Can be deployed as:
- Cron job (Linux/Mac)
- Task Scheduler (Windows)
- Docker + orchestration
- Always-running daemon
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "meta_learner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LearnerScheduler:
    """Schedule meta learning tasks."""
    
    def __init__(
        self,
        interval_hours: int = 6,
        dry_run: bool = False
    ):
        """Initialize scheduler.
        
        Args:
            interval_hours: Hours between learning runs (default 6)
            dry_run: If True, don't actually update meta
        """
        self.interval = timedelta(hours=interval_hours)
        self.dry_run = dry_run
        self.last_run: datetime = None
        self.last_patch: str = None
    
    def should_run(self) -> bool:
        """Check if learning should run now.
        
        Returns True if:
        - First run
        - Interval has passed
        - Patch updated
        
        Returns:
            True if should run
        """
        # First run
        if self.last_run is None:
            return True
        
        # Interval check
        if datetime.now() - self.last_run >= self.interval:
            return True
        
        return False
    
    def run_learning(self) -> bool:
        """Run meta learning cycle.
        
        Returns:
            True if successful
        """
        logger.info("=" * 50)
        logger.info("Starting meta learning cycle")
        
        try:
            from meta_learner import MetaLearner, MetaPatcher
            
            if self.dry_run:
                logger.info("[DRY RUN] Would analyze meta here")
                return True
            
            # Check patch
            current_patch = MetaPatcher.get_current_patch()
            logger.info(f"Current patch: {current_patch}")
            
            if current_patch == self.last_patch:
                logger.info("Same patch as last run, skipping")
                return True
            
            # Run learner
            logger.info("Starting meta learner...")
            learner = MetaLearner(platform="na1")
            learner.learn_from_matches(matches_per_player=5, num_players=20)
            learner.update_meta_database()
            
            # Update patch
            meta_version = len(learner.calculate_meta_scores())
            MetaPatcher.save_patch_info(current_patch, meta_version)
            self.last_patch = current_patch
            
            logger.info("✓ Meta learning successful")
            return True
            
        except Exception as e:
            logger.error(f"✗ Meta learning failed: {e}", exc_info=True)
            return False
        finally:
            self.last_run = datetime.now()
            logger.info(f"Next run scheduled: {self.last_run + self.interval}")
    
    def run_continuous(self, check_interval_seconds: int = 60) -> None:
        """Run scheduler continuously (blocking).
        
        Args:
            check_interval_seconds: Check every N seconds if should run
        """
        logger.info(f"Starting scheduler (check every {check_interval_seconds}s)")
        logger.info(f"Learning interval: {self.interval}")
        
        try:
            while True:
                if self.should_run():
                    self.run_learning()
                
                time.sleep(check_interval_seconds)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            raise


def run_once() -> bool:
    """Run meta learning once and exit.
    
    Usage: python learner_scheduler.py once
    
    Returns:
        True if successful
    """
    scheduler = LearnerScheduler()
    success = scheduler.run_learning()
    return success


def run_daemon(interval_hours: int = 6, check_seconds: int = 60) -> None:
    """Run scheduler as daemon (continuously).
    
    Usage: python learner_scheduler.py daemon [interval_hours] [check_seconds]
    
    Args:
        interval_hours: Hours between learning runs
        check_seconds: Seconds between checks
    """
    scheduler = LearnerScheduler(interval_hours=interval_hours)
    scheduler.run_continuous(check_interval_seconds=check_seconds)


def run_test() -> None:
    """Test mode - dry run without updating meta.
    
    Usage: python learner_scheduler.py test
    """
    scheduler = LearnerScheduler(dry_run=True)
    scheduler.run_learning()


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        mode = "daemon"
    else:
        mode = sys.argv[1]
    
    if mode == "once":
        success = run_once()
        sys.exit(0 if success else 1)
    
    elif mode == "test":
        run_test()
        sys.exit(0)
    
    elif mode == "daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        check = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        run_daemon(interval_hours=interval, check_seconds=check)
    
    else:
        print(f"Unknown mode: {mode}")
        print("\nUsage:")
        print("  python learner_scheduler.py once       - Run once and exit")
        print("  python learner_scheduler.py test       - Test dry run")
        print("  python learner_scheduler.py daemon [hours] [seconds]")
        print("    -> Run continuously (check every N seconds)")
        sys.exit(1)


if __name__ == "__main__":
    main()
