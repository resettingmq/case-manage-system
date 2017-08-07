# 1. 更新关联的payable.unsettled_amount
#     这里不做验证，验证放在modelform中

DROP TRIGGER IF EXISTS payment_before_insert;

DELIMITER //
CREATE TRIGGER payment_before_insert BEFORE INSERT
  ON purchase_payment
  FOR EACH ROW
BEGIN
  IF NEW.enabled = 1 THEN
    UPDATE purchase_payable
      SET unsettled_amount = unsettled_amount - NEW.amount
      WHERE id = NEW.payable_id;
  END IF;
END //
DELIMITER ;


# 1. 在更新amount的时候，根据增量更新关联payable.unsettled_amount
#     这里不做验证，验证放在modelform中
# 2. enabled从1变为0时，更新关联payable.unsettled_amount
#
# payment的update有几种情况
# 1. 修改amount
# 2. 修改payable_id（在前端实现中禁止了这种修改方式）
# 3. 修改enabled（在前端逻辑中只允许从1->0

DROP TRIGGER IF EXISTS payment_before_update;

DELIMITER //
CREATE TRIGGER payment_before_update BEFORE UPDATE
  ON purchase_payment
  FOR EACH ROW
begin_payment_before_update: BEGIN

  IF NEW.enabled = 0 AND OLD.enabled = 1 THEN
    SET NEW.amount = OLD.amount;
    UPDATE purchase_payable
      SET unsettled_amount = unsettled_amount + OLD.amount
      WHERE id = OLD.payable_id;
    LEAVE begin_payment_before_update;
  END IF;

  SET @amount_delta = NEW.amount - OLD.amount;
  IF @amount_delta != 0 THEN
    -- 因为在form中保证了payable不能更改
    -- 所以update中可以使用OLD.payable_id或者NEW.payable_id
    UPDATE purchase_payable
      SET unsettled_amount = unsettled_amount - @amount_delta
      WHERE id = OLD.payable_id;
  END IF;

END begin_payment_before_update//
DELIMITER ;


# 1. 在删除的时候，更新关联payable.amount

DROP TRIGGER IF EXISTS payment_before_delete;

DELIMITER //
CREATE TRIGGER payment_before_delete BEFORE DELETE
  ON purchase_payment
  FOR EACH ROW
BEGIN
  UPDATE purchase_payable
    SET unsettled_amount = unsettled_amount + OLD.amount
    WHERE id = old.payable_id;
END //
DELIMITER ;
