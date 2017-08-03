# 1. 更新关联的receivable.unsettled_amount
#     这里不做验证，验证放在modelform中

DROP TRIGGER IF EXISTS receipts_before_insert;

DELIMITER //
CREATE TRIGGER receipts_before_insert BEFORE INSERT
  ON sale_receipts
  FOR EACH ROW
BEGIN
  IF NEW.enabled = 1 THEN
    UPDATE sale_receivable
      SET unsettled_amount = unsettled_amount - NEW.amount
      WHERE id = NEW.receivable_id;
  END IF;
END //
DELIMITER ;


# 1. 在更新amount的时候，根据增量更新关联receivable.unsettled_amount
#     这里不做验证，验证放在modelform中
# 2. enabled从1变为0时，更新关联receivable.unsettled_amount
#
# reciepts的update有几种情况
# 1. 修改amount
# 2. 修改receivable_id
# 3. 修改enabled

DROP TRIGGER IF EXISTS receipts_before_update;

DELIMITER //
CREATE TRIGGER receipts_before_update BEFORE UPDATE
  ON sale_receipts
  FOR EACH ROW
begin_receipts_before_update: BEGIN

  IF NEW.enabled = 0 AND OLD.enabled = 1 THEN
    SET NEW.amount = OLD.amount;
    UPDATE sale_receivable
      SET unsettled_amount = unsettled_amount + OLD.amount
      WHERE id = OLD.receivable_id;
    LEAVE begin_receipts_before_update;
  END IF;

  SET @amount_delta = NEW.amount - OLD.amount;
  IF @amount_delta != 0 THEN
    -- 因为在form中保证了receivable不能更改
    -- 所以update中可以使用OLD.receivable_id或者NEW.receivable_id
    UPDATE sale_receivable
      SET unsettled_amount = unsettled_amount - @amount_delta
      WHERE id = OLD.receivable_id;
  END IF;

END begin_receipts_before_update//
DELIMITER ;


# 1. 在删除的时候，更新关联receivable.amount

DROP TRIGGER IF EXISTS receipts_before_delete;

DELIMITER //
CREATE TRIGGER receipts_before_delete BEFORE DELETE
  ON sale_receipts
  FOR EACH ROW
BEGIN
  UPDATE sale_receivable
    SET unsettled_amount = unsettled_amount + OLD.amount
    WHERE id = old.receivable_id;
END //
DELIMITER ;
