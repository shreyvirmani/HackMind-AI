from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, timedelta

from .models import (
    Project,
    Subscription,
    Payment,
    FREE_PLAN_WEEKLY_GENERATION_LIMIT,
    GENERATION_WINDOW_DAYS,
)


class SubscriptionRepository:

    def get_or_create(self, db: Session, user_id: str) -> Subscription:
        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .first()
        )

        if sub:
            return sub

        # First time we've seen this user -- give them the Free plan,
        # with a fresh weekly generation window starting now.
        sub = Subscription(
            user_id=user_id,
            plan="free",
            status="active",
            generations_used=0,
            generation_window_start=datetime.utcnow(),
        )

        db.add(sub)
        db.commit()
        db.refresh(sub)

        return sub

    def reset_window_if_needed(
        self,
        db: Session,
        sub: Subscription
    ) -> Subscription:
        """
        Free-plan generations are capped per rolling 7-day window,
        not lifetime. If the current window has expired, reset the
        counter and start a new window from now.
        """

        window_start = (
            sub.generation_window_start
            or sub.created_at
            or datetime.utcnow()
        )

        if (
            datetime.utcnow() - window_start
            >= timedelta(days=GENERATION_WINDOW_DAYS)
        ):
            sub.generations_used = 0
            sub.generation_window_start = datetime.utcnow()

            db.commit()
            db.refresh(sub)

        return sub

    def increment_generations_used(
        self,
        db: Session,
        user_id: str
    ) -> Subscription:

        sub = self.get_or_create(db, user_id)
        sub = self.reset_window_if_needed(db, sub)

        sub.generations_used = (
            sub.generations_used or 0
        ) + 1

        db.commit()
        db.refresh(sub)

        return sub

    def upgrade_to_pro(
        self,
        db: Session,
        user_id: str,
        months: int = 1
    ) -> Subscription:

        sub = self.get_or_create(db, user_id)

        sub.plan = "pro"
        sub.status = "active"
        sub.expires_at = (
            datetime.utcnow()
            + timedelta(days=30 * months)
        )

        db.commit()
        db.refresh(sub)

        return sub

    def expire_if_needed(
        self,
        db: Session,
        sub: Subscription
    ) -> Subscription:

        """
        Pro plans are time-boxed -- if expires_at has passed,
        drop back to Free instead of silently keeping Pro access forever.
        """

        if (
            sub.plan == "pro"
            and sub.expires_at is not None
            and sub.expires_at < datetime.utcnow()
        ):
            sub.plan = "free"
            sub.status = "expired"

            db.commit()
            db.refresh(sub)

        return sub


subscription_repository = SubscriptionRepository()


class PaymentRepository:

    def create_order_record(
        self,
        db: Session,
        user_id: str,
        razorpay_order_id: str,
        amount: int,
        currency: str = "INR",
    ) -> Payment:

        payment = Payment(
            user_id=user_id,
            razorpay_order_id=razorpay_order_id,
            amount=amount,
            currency=currency,
            status="created",
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    def get_by_order_id(
        self,
        db: Session,
        razorpay_order_id: str
    ) -> Payment:

        return (
            db.query(Payment)
            .filter(
                Payment.razorpay_order_id
                == razorpay_order_id
            )
            .first()
        )

    def mark_paid(
        self,
        db: Session,
        razorpay_order_id: str,
        razorpay_payment_id: str
    ) -> Payment:

        payment = self.get_by_order_id(
            db,
            razorpay_order_id
        )

        if payment:
            payment.status = "paid"
            payment.razorpay_payment_id = (
                razorpay_payment_id
            )

            db.commit()
            db.refresh(payment)

        return payment

    def mark_failed(
        self,
        db: Session,
        razorpay_order_id: str
    ) -> Payment:

        payment = self.get_by_order_id(
            db,
            razorpay_order_id
        )

        if payment:
            payment.status = "failed"

            db.commit()
            db.refresh(payment)

        return payment


payment_repository = PaymentRepository()


class ProjectRepository:

    def create_project(
        self,
        db: Session,
        user_id: str,
        project_title: str,
        idea: str,
        roadmap: dict,
        research: dict,
        judge: dict,
        pitch_deck: dict,
        architecture: dict | None = None,
    ):

        overall_score = (
            judge.get("overall_score", 0)
            if isinstance(judge, dict)
            else 0
        )

        project = Project(
            user_id=user_id,
            project_title=project_title,
            idea=idea,
            roadmap=roadmap,
            research=research,
            architecture=architecture or {},
            judge=judge,
            pitch_deck=pitch_deck,
            overall_score=overall_score,
        )

        db.add(project)

        db.commit()

        db.refresh(project)

        return project

    def get_all_projects(
        self,
        db: Session,
        user_id: str,
    ):

        return (
            db.query(Project)
            .filter(
                Project.user_id == user_id
            )
            .order_by(
                Project.created_at.desc()
            )
            .all()
        )

    def get_project(
        self,
        db: Session,
        project_id: int,
        user_id: str,
    ):

        return (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == user_id,
            )
            .first()
        )

    def update_project_section(
        self,
        db: Session,
        project_id: int,
        user_id: str,
        section: str,
        updated_data: dict,
    ):

        project = self.get_project(
            db,
            project_id,
            user_id,
        )

        if not project:
            return None

        if section == "roadmap":

            current_data = project.roadmap or {}

            current_data.update(
                updated_data
            )

            project.roadmap = current_data

            flag_modified(
                project,
                "roadmap"
            )

        elif section == "research":

            current_data = project.research or {}

            current_data.update(
                updated_data
            )

            project.research = current_data

            flag_modified(
                project,
                "research"
            )

        elif section == "architecture":

            current_data = (
                project.architecture or {}
            )

            current_data.update(
                updated_data
            )

            project.architecture = current_data

            flag_modified(
                project,
                "architecture"
            )

        elif section == "judge":

            current_data = project.judge or {}

            current_data.update(
                updated_data
            )

            project.judge = current_data

            flag_modified(
                project,
                "judge"
            )

        elif section == "pitch_deck":

            current_data = (
                project.pitch_deck or {}
            )

            current_data.update(
                updated_data
            )

            project.pitch_deck = current_data

            flag_modified(
                project,
                "pitch_deck"
            )

        else:

            raise ValueError(
                f"Invalid section: {section}"
            )

        db.commit()

        db.refresh(project)

        return project

    def delete_project(
        self,
        db: Session,
        project_id: int,
        user_id: str,
    ):

        project = self.get_project(
            db,
            project_id,
            user_id,
        )

        if project:

            db.delete(project)

            db.commit()

        return project


project_repository = ProjectRepository()